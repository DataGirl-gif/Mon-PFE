from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count
from django.db.models.functions import TruncMonth
import json
from .forms import PatientForm, VisiteForm
from .models import Patient, Visite, Analyse, VisiteAnalyse

# --- SECTION AUTHENTIFICATION ---

@login_required
def page_connexion_reussie(request):
    """Après le login, tout le personnel est redirigé vers le tableau de bord"""
    return redirect('tableau_de_bord')

def deconnexion_utilisateur(request):
    logout(request)
    return redirect('login')

# --- SECTION TABLEAU DE BORD ---

@login_required
def tableau_de_bord(request):
    # 1. KPIs
    total_visites = Visite.objects.count()
    examens_valides = Visite.objects.filter(statut='VALIDE').count()
    en_attente = Visite.objects.filter(statut='EN_COURS').count()

    # 2. Graphique Linéaire (Évolution)
    visites_stats = Visite.objects.annotate(month=TruncMonth('date_visite')) \
        .values('month').annotate(count=Count('id')).order_by('month')
    
    labels_evolution = [v['month'].strftime('%b %Y') for v in visites_stats]
    data_evolution = [v['count'] for v in visites_stats]

    # 3. Répartition (Donut)
    statuts_data = [en_attente, examens_valides]

    # 4. Derniers patients pour le graphique horizontal
    # On utilise 'examens' car c'est le 'related_name' défini dans ton modèle VisiteAnalyse
    derniers_visites = Visite.objects.all().select_related('patient') \
        .annotate(nb_examens=Count('examens')) \
        .order_by('-id')[:5]
    
    labels_patients = [v.patient.nom for v in derniers_visites]
    data_examens = [v.nb_examens for v in derniers_visites]

    context = {
        'total_visites': total_visites,
        'examens_valides': examens_valides,
        'en_attente': en_attente,
        'labels_evolution': json.dumps(labels_evolution),
        'data_evolution': json.dumps(data_evolution),
        'statuts_data': json.dumps(statuts_data),
        'labels_patients': json.dumps(labels_patients),
        'data_examens': json.dumps(data_examens),
    }
    return render(request, 'core/dashboard.html', context)
# --- SECTION PATIENTS & VISITES ---

@login_required
def interface_principale_laboratoire(request):
    query = request.GET.get('search_query', '').strip()
    resultats_patients = None
    
    if query:
        resultats_patients = Patient.objects.filter(nom__icontains=query) | Patient.objects.filter(prenom__icontains=query)

    if request.method == 'POST':
        form_patient = PatientForm(request.POST)
        form_visite = VisiteForm(request.POST)

        if form_patient.is_valid() and form_visite.is_valid():
            patient = form_patient.save()
            visite = form_visite.save(commit=False)
            visite.patient = patient
            visite.save()
            messages.success(request, f"Patient {patient.nom.upper()} enregistré. Dossier N° {visite.id}.")
            return redirect('gestion_examens_visite', visite_id=visite.id)
    else:
        form_patient = PatientForm()
        form_visite = VisiteForm()

    toutes_les_visites = Visite.objects.all().select_related('patient').order_by('-id')
    context = {
        'form_patient': form_patient,
        'form_visite': form_visite,
        'resultats_patients': resultats_patients,
        'toutes_les_visites': toutes_les_visites,
        'search_query': query,
    }
    return render(request, 'core/interface_principale.html', context)

@login_required
def gestion_examens_visite(request, visite_id):
    visite = get_object_or_404(Visite, id=visite_id)
    
    if request.method == 'POST':
        if 'ajouter_analyse' in request.POST:
            analyse_id = request.POST.get('analyse_choisie')
            if analyse_id:
                analyse = get_object_or_404(Analyse, id=analyse_id)
                if not VisiteAnalyse.objects.filter(visite=visite, analyse=analyse).exists():
                    VisiteAnalyse.objects.create(visite=visite, analyse=analyse)
                    messages.success(request, f"Examen {analyse.nom} ajouté.")
            return redirect('gestion_examens_visite', visite_id=visite.id)

        if 'sauvegarder_resultat' in request.POST:
            ligne_id = request.POST.get('ligne_id')
            valeur = request.POST.get('valeur_resultat', '').strip()
            if ligne_id:
                ligne_examen = get_object_or_404(VisiteAnalyse, id=ligne_id)
                ligne_examen.valeur_resultat = valeur
                ligne_examen.saisi_par = request.user
                ligne_examen.save()
                messages.success(request, "Résultat enregistré.")
            return redirect('gestion_examens_visite', visite_id=visite.id)

        if 'supprimer_ligne' in request.POST:
            ligne_id = request.POST.get('ligne_id')
            if ligne_id:
                get_object_or_404(VisiteAnalyse, id=ligne_id).delete()
                messages.warning(request, "Examen retiré.")
            return redirect('gestion_examens_visite', visite_id=visite.id)

        if 'valider_visite' in request.POST:
            visite.statut = 'VALIDE'
            visite.valide_par = request.user
            visite.save()
            messages.success(request, "Visite validée.")
            return redirect('gestion_examens_visite', visite_id=visite.id)

    analyses_catalogue = Analyse.objects.all().order_by('nom')
    examens_patient = VisiteAnalyse.objects.filter(visite=visite).select_related('analyse')

    context = {
        'visite': visite,
        'analyses_catalogue': analyses_catalogue,
        'examens_patient': examens_patient,
    }
    return render(request, 'core/gestion_examens.html', context)

# --- SECTION IMPRESSIONS ---

@login_required
def imprimer_recu_facture(request, visite_id):
    visite = get_object_or_404(Visite, id=visite_id)
    examens = VisiteAnalyse.objects.filter(visite=visite).select_related('analyse')
    frais_brut = sum(float(item.analyse.prix or 0) for item in examens)
    reduction = frais_brut * (visite.taux_reduction / 100)
    frais_net = frais_brut - reduction
    net_a_payer = frais_net + float(visite.majoration) + float(visite.deplacement)
    context = {'visite': visite, 'examens': examens, 'frais_brut': f"{frais_brut:.2f}", 'net_a_payer': f"{net_a_payer:.2f}", 'date_actuelle': timezone.now().strftime("%d/%m/%Y")}
    return render(request, 'core/facture_recu.html', context)

@login_required
def imprimer_bulletin_resultats(request, visite_id):
    visite = get_object_or_404(Visite, id=visite_id)
    examens = VisiteAnalyse.objects.filter(visite=visite).select_related('analyse')
    context = {'visite': visite, 'examens': examens, 'date_actuelle': timezone.now().strftime("%d/%m/%Y")}
    return render(request, 'core/bulletin_resultats.html', context)

# --- SECTION GESTION CATALOGUE ---

@login_required
def liste_examens(request):
    analyses = Analyse.objects.all().order_by('nom')
    return render(request, 'core/liste_examens.html', {'analyses': analyses})

@login_required
def modifier_examen_catalogue(request, analyse_id):
    analyse = get_object_or_404(Analyse, id=analyse_id)
    if request.method == 'POST':
        analyse.nom = request.POST.get('nom')
        analyse.prix = request.POST.get('prix')
        analyse.unite = request.POST.get('unite')
        analyse.valeurs_normales = request.POST.get('valeurs_normales')
        analyse.save()
        messages.success(request, f"Examen {analyse.nom} mis à jour.")
    return redirect('liste_examens')

@login_required
def ajouter_nouvel_examen(request):
    if request.method == 'POST':
        Analyse.objects.create(
            nom=request.POST.get('nom'),
            prix=request.POST.get('prix'),
            unite=request.POST.get('unite'),
            valeurs_normales=request.POST.get('valeurs_normales')
        )
        messages.success(request, "Nouvel examen ajouté.")
        return redirect('liste_examens')
    return render(request, 'core/ajouter_examen.html')

@login_required
def liste_visites(request):
    visites = Visite.objects.all().select_related('patient').order_by('-date_visite')
    return render(request, 'core/liste_visites.html', {'visites': visites})

@login_required
def supprimer_visite(request, visite_id):
    visite = get_object_or_404(Visite, id=visite_id)
    visite.delete()
    messages.warning(request, "Visite supprimée.")
    return redirect('liste_visites')

@login_required
def liste_fiches_techniques(request):
    fiches = VisiteAnalyse.objects.all().select_related('visite', 'visite__patient', 'analyse').order_by('-id')
    return render(request, 'core/liste_fiches.html', {'fiches': fiches})