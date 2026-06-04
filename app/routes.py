from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from app import db, bcrypt
from app.models import Utilisateur, Filiere, Matiere, Annonce, Matching, Conversation, Message, ParticipantConversation

main = Blueprint('main', __name__)

# Page d'accueil
@main.route('/')
def index():
    return render_template('index.html')

# Inscription
@main.route('/inscription', methods=['GET', 'POST'])
def inscription():
    if request.method == 'POST':
        nom = request.form['nom']
        prenom = request.form['prenom']
        email = request.form['email']
        telephone = request.form['telephone']
        mot_de_passe = request.form['mot_de_passe']

        # Vérifier si email ou téléphone existe déjà
        if Utilisateur.query.filter_by(email=email).first():
            return jsonify({'erreur': 'Email déjà utilisé'}), 400
        if Utilisateur.query.filter_by(telephone=telephone).first():
            return jsonify({'erreur': 'Téléphone déjà utilisé'}), 400

        # Hasher le mot de passe
        hash_mdp = bcrypt.generate_password_hash(mot_de_passe).decode('utf-8')

        # Créer l'utilisateur
        nouvel_utilisateur = Utilisateur(
            nom=nom,
            prenom=prenom,
            email=email,
            telephone=telephone,
            mot_de_passe_hash=hash_mdp
        )
        db.session.add(nouvel_utilisateur)
        db.session.commit()
        return redirect(url_for('main.connexion'))
    
    filieres = Filiere.query.all()
    return render_template('inscription.html', filieres=filieres)

# Connexion
@main.route('/connexion', methods=['GET', 'POST'])
def connexion():
    if request.method == 'POST':
        identifiant = request.form['identifiant']
        mot_de_passe = request.form['mot_de_passe']

        utilisateur = Utilisateur.query.filter(
            (Utilisateur.email == identifiant) | 
            (Utilisateur.telephone == identifiant)
        ).first()

        if utilisateur and bcrypt.check_password_hash(utilisateur.mot_de_passe_hash, mot_de_passe):
            session['utilisateur_id'] = utilisateur.id
            session['utilisateur_nom'] = utilisateur.prenom
            return redirect(url_for('main.tableau_de_bord'))
        else:
            return render_template('connexion.html', erreur='Identifiant ou mot de passe incorrect')

    return render_template('connexion.html')

# Déconnexion
@main.route('/deconnexion')
def deconnexion():
    session.clear()
    return redirect(url_for('main.index'))

# Tableau de bord
@main.route('/tableau-de-bord')
def tableau_de_bord():
    if 'utilisateur_id' not in session:
        return redirect(url_for('main.connexion'))
    utilisateur = Utilisateur.query.get(session['utilisateur_id'])
    return render_template('tableau_de_bord.html', utilisateur=utilisateur)
# Publier une annonce
@main.route('/annonce', methods=['GET', 'POST'])
def annonce():
    if 'utilisateur_id' not in session:
        return redirect(url_for('main.connexion'))
    
    if request.method == 'POST':
        type_annonce = request.form['type_annonce']
        matiere_id = request.form['matiere_id']
        format = request.form['format']
        description = request.form['description']

        nouvelle_annonce = Annonce(
            utilisateur_id=session['utilisateur_id'],
            type_annonce=type_annonce,
            matiere_id=matiere_id,
            format=format,
            description=description
        )
        db.session.add(nouvelle_annonce)
        db.session.commit()
        return redirect(url_for('main.tableau_de_bord'))

    matieres = Matiere.query.all()
    return render_template('annonce.html', matieres=matieres)
# Matching
@main.route('/matching')
def matching():
    if 'utilisateur_id' not in session:
        return redirect(url_for('main.connexion'))
    
    utilisateur = Utilisateur.query.get(session['utilisateur_id'])
    
    # Récupérer tous les autres utilisateurs
    tous_utilisateurs = Utilisateur.query.filter(
        Utilisateur.id != session['utilisateur_id']
    ).all()
    
    # Algorithme de matching
    matchs = []
    for autre in tous_utilisateurs:
        score = 0
        
        # Même filière = +40 points
        if utilisateur.filiere_id and autre.filiere_id:
            if utilisateur.filiere_id == autre.filiere_id:
                score += 40
        
        # Même niveau = +30 points
        if utilisateur.niveau_etudes and autre.niveau_etudes:
            if utilisateur.niveau_etudes == autre.niveau_etudes:
                score += 30
        
        # A des annonces actives = +30 points
        annonces = Annonce.query.filter_by(
            utilisateur_id=autre.id,
            est_active=True
        ).count()
        if annonces > 0:
            score += 30
        
        if score > 0:
            matchs.append({
                'utilisateur': autre,
                'score': score
            })
    
    # Trier par score décroissant
    matchs.sort(key=lambda x: x['score'], reverse=True)
    
    return render_template('matching.html', matchs=matchs)
# Liste des conversations
@main.route('/messagerie')
def messagerie():
    if 'utilisateur_id' not in session:
        return redirect(url_for('main.connexion'))
    
    # Récupérer toutes les conversations de l'utilisateur
    participations = ParticipantConversation.query.filter_by(
        utilisateur_id=session['utilisateur_id']
    ).all()
    
    conversations = []
    for p in participations:
        conv = Conversation.query.get(p.conversation_id)
        # Dernier message
        dernier_message = Message.query.filter_by(
            conversation_id=conv.id
        ).order_by(Message.date_envoi.desc()).first()
        
        # Autre participant
        autre_participant = ParticipantConversation.query.filter(
            ParticipantConversation.conversation_id == conv.id,
            ParticipantConversation.utilisateur_id != session['utilisateur_id']
        ).first()
        
        autre_utilisateur = None
        if autre_participant:
            autre_utilisateur = Utilisateur.query.get(autre_participant.utilisateur_id)
        
        conversations.append({
            'conversation': conv,
            'dernier_message': dernier_message,
            'autre_utilisateur': autre_utilisateur
        })
    
    return render_template('messagerie.html', conversations=conversations)

# Ouvrir une conversation
@main.route('/conversation/<int:autre_id>', methods=['GET', 'POST'])
def conversation(autre_id):
    if 'utilisateur_id' not in session:
        return redirect(url_for('main.connexion'))
    
    autre_utilisateur = Utilisateur.query.get_or_404(autre_id)
    
    # Chercher une conversation existante entre les deux
    conv = None
    mes_convs = ParticipantConversation.query.filter_by(
        utilisateur_id=session['utilisateur_id']
    ).all()
    
    for p in mes_convs:
        autre = ParticipantConversation.query.filter_by(
            conversation_id=p.conversation_id,
            utilisateur_id=autre_id
        ).first()
        if autre:
            conv = Conversation.query.get(p.conversation_id)
            break
    
    # Créer une nouvelle conversation si elle n'existe pas
    if not conv:
        conv = Conversation()
        db.session.add(conv)
        db.session.flush()
        
        p1 = ParticipantConversation(
            conversation_id=conv.id,
            utilisateur_id=session['utilisateur_id']
        )
        p2 = ParticipantConversation(
            conversation_id=conv.id,
            utilisateur_id=autre_id
        )
        db.session.add(p1)
        db.session.add(p2)
        db.session.commit()
    
    # Envoyer un message
    if request.method == 'POST':
        contenu = request.form['contenu']
        if contenu.strip():
            msg = Message(
                conversation_id=conv.id,
                expediteur_id=session['utilisateur_id'],
                contenu=contenu
            )
            db.session.add(msg)
            db.session.commit()
        return redirect(url_for('main.conversation', autre_id=autre_id))
    
    # Récupérer tous les messages
    messages = Message.query.filter_by(
        conversation_id=conv.id
    ).order_by(Message.date_envoi.asc()).all()
    
    return render_template('conversation.html', 
                         autre_utilisateur=autre_utilisateur,
                         messages=messages,
                         conversation=conv,
                         utilisateur_id=session['utilisateur_id'])
# Profil utilisateur
@main.route('/profil', methods=['GET', 'POST'])
def profil():
    if 'utilisateur_id' not in session:
        return redirect(url_for('main.connexion'))
    
    utilisateur = Utilisateur.query.get(session['utilisateur_id'])
    
    if request.method == 'POST':
        utilisateur.bio = request.form.get('bio')
        utilisateur.niveau_etudes = request.form.get('niveau_etudes')
        utilisateur.filiere_id = request.form.get('filiere_id')
        
        db.session.commit()
        return redirect(url_for('main.profil'))
    
    filieres = Filiere.query.all()
    matieres = Matiere.query.all()
    return render_template('profil.html', 
                         utilisateur=utilisateur,
                         filieres=filieres,
                         matieres=matieres)