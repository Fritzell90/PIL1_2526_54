from app import db
from datetime import datetime

class Filiere(db.Model):
    __tablename__ = 'filieres'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), nullable=False, unique=True)
    libelle = db.Column(db.String(100), nullable=False)

class Matiere(db.Model):
    __tablename__ = 'matieres'
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)

class Utilisateur(db.Model):
    __tablename__ = 'utilisateurs'
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    telephone = db.Column(db.String(20), nullable=False, unique=True)
    mot_de_passe_hash = db.Column(db.String(255), nullable=False)
    photo_profil = db.Column(db.String(255))
    bio = db.Column(db.Text)
    filiere_id = db.Column(db.Integer, db.ForeignKey('filieres.id'))
    niveau_etudes = db.Column(db.String(20))
    est_actif = db.Column(db.Boolean, default=True)
    date_inscription = db.Column(db.DateTime, default=datetime.utcnow)
    derniere_connexion = db.Column(db.DateTime)

class Annonce(db.Model):
    __tablename__ = 'annonces'
    id = db.Column(db.Integer, primary_key=True)
    utilisateur_id = db.Column(db.Integer, db.ForeignKey('utilisateurs.id'), nullable=False)
    type_annonce = db.Column(db.String(10), nullable=False)
    matiere_id = db.Column(db.Integer, db.ForeignKey('matieres.id'), nullable=False)
    format = db.Column(db.String(10), nullable=False)
    description = db.Column(db.Text)
    est_active = db.Column(db.Boolean, default=True)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    matiere = db.relationship('Matiere', backref='annonces')

class Matching(db.Model):
    __tablename__ = 'matchings'
    id = db.Column(db.Integer, primary_key=True)
    mentor_id = db.Column(db.Integer, db.ForeignKey('utilisateurs.id'), nullable=False)
    mentore_id = db.Column(db.Integer, db.ForeignKey('utilisateurs.id'), nullable=False)
    score_compatibilite = db.Column(db.Numeric(5,2))
    statut = db.Column(db.String(20), default='propose')
    date_matching = db.Column(db.DateTime, default=datetime.utcnow)

class Conversation(db.Model):
    __tablename__ = 'conversations'
    id = db.Column(db.Integer, primary_key=True)
    matching_id = db.Column(db.Integer, db.ForeignKey('matchings.id'))
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)

class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversations.id'), nullable=False)
    expediteur_id = db.Column(db.Integer, db.ForeignKey('utilisateurs.id'), nullable=False)
    contenu = db.Column(db.Text, nullable=False)
    est_lu = db.Column(db.Boolean, default=False)
    date_envoi = db.Column(db.DateTime, default=datetime.utcnow)
class ParticipantConversation(db.Model):
    __tablename__ = 'participants_conversation'
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversations.id'), nullable=False)
    utilisateur_id = db.Column(db.Integer, db.ForeignKey('utilisateurs.id'), nullable=False)
    date_rejoins = db.Column(db.DateTime, default=datetime.utcnow)
class Disponibilite(db.Model):
    __tablename__ = 'disponibilites'
    id = db.Column(db.Integer, primary_key=True)
    utilisateur_id = db.Column(db.Integer, db.ForeignKey('utilisateurs.id'), nullable=False)
    jour_semaine = db.Column(db.String(10), nullable=False)
    heure_debut = db.Column(db.Time, nullable=False)
    heure_fin = db.Column(db.Time, nullable=False)