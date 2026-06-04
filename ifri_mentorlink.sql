-- ============================================================
--  IFRI_MentorLink — Schéma PostgreSQL
--  Projet intégrateur PIL1 2025-2026
-- ============================================================

-- Extensions utiles
CREATE EXTENSION IF NOT EXISTS "pgcrypto"; -- pour gen_random_uuid()

-- ============================================================
-- 1. FILIÈRES ET MATIÈRES (données de référence)
-- ============================================================

CREATE TABLE filieres (
    id          SERIAL PRIMARY KEY,
    code        VARCHAR(20)  NOT NULL UNIQUE,  -- ex: 'IA', 'GL', 'IM', 'SI', 'SE_IOT'
    libelle     VARCHAR(100) NOT NULL           -- ex: 'Intelligence Artificielle'
);

CREATE TABLE matieres (
    id          SERIAL PRIMARY KEY,
    nom         VARCHAR(100) NOT NULL UNIQUE,   -- ex: 'Algorithmique', 'Python'
    description TEXT
);


-- ============================================================
-- 2. UTILISATEURS ET PROFILS
-- ============================================================

CREATE TABLE utilisateurs (
    id                  SERIAL PRIMARY KEY,
    nom                 VARCHAR(100) NOT NULL,
    prenom              VARCHAR(100) NOT NULL,
    email               VARCHAR(255) NOT NULL UNIQUE,
    telephone           VARCHAR(20)  NOT NULL UNIQUE,
    mot_de_passe_hash   VARCHAR(255) NOT NULL,          -- mot de passe hashé (bcrypt)
    photo_profil        VARCHAR(255),                   -- chemin ou URL de la photo
    bio                 TEXT,                           -- courte biographie
    filiere_id          INT REFERENCES filieres(id) ON DELETE SET NULL,
    niveau_etudes       VARCHAR(20) CHECK (niveau_etudes IN ('L1','L2','L3','M1','M2')),
    est_actif           BOOLEAN     NOT NULL DEFAULT TRUE,
    date_inscription    TIMESTAMP   NOT NULL DEFAULT NOW(),
    derniere_connexion  TIMESTAMP
);

-- Compétences (matières maîtrisées) d'un utilisateur
CREATE TABLE competences_utilisateur (
    id              SERIAL PRIMARY KEY,
    utilisateur_id  INT NOT NULL REFERENCES utilisateurs(id) ON DELETE CASCADE,
    matiere_id      INT NOT NULL REFERENCES matieres(id)     ON DELETE CASCADE,
    niveau          SMALLINT CHECK (niveau BETWEEN 1 AND 5), -- 1=débutant, 5=expert
    UNIQUE (utilisateur_id, matiere_id)
);

-- Lacunes (matières où l'utilisateur a besoin d'aide)
CREATE TABLE lacunes_utilisateur (
    id              SERIAL PRIMARY KEY,
    utilisateur_id  INT NOT NULL REFERENCES utilisateurs(id) ON DELETE CASCADE,
    matiere_id      INT NOT NULL REFERENCES matieres(id)     ON DELETE CASCADE,
    UNIQUE (utilisateur_id, matiere_id)
);

-- Disponibilités habituelles (ex: Lundi 08h-10h)
CREATE TABLE disponibilites (
    id              SERIAL PRIMARY KEY,
    utilisateur_id  INT NOT NULL REFERENCES utilisateurs(id) ON DELETE CASCADE,
    jour_semaine    VARCHAR(10) NOT NULL CHECK (
                        jour_semaine IN ('Lundi','Mardi','Mercredi','Jeudi','Vendredi','Samedi','Dimanche')
                    ),
    heure_debut     TIME NOT NULL,
    heure_fin       TIME NOT NULL,
    CHECK (heure_fin > heure_debut)
);


-- ============================================================
-- 3. OFFRES ET DEMANDES DE MENTORAT
-- ============================================================

CREATE TABLE annonces (
    id              SERIAL PRIMARY KEY,
    utilisateur_id  INT  NOT NULL REFERENCES utilisateurs(id) ON DELETE CASCADE,
    type_annonce    VARCHAR(10) NOT NULL CHECK (type_annonce IN ('offre', 'demande')),
    matiere_id      INT  NOT NULL REFERENCES matieres(id)     ON DELETE CASCADE,
    format          VARCHAR(10) NOT NULL CHECK (format IN ('presentiel','en_ligne','les_deux')),
    description     TEXT,
    est_active      BOOLEAN   NOT NULL DEFAULT TRUE,
    date_creation   TIMESTAMP NOT NULL DEFAULT NOW(),
    date_expiration TIMESTAMP
);

-- Disponibilités spécifiques rattachées à une annonce
CREATE TABLE disponibilites_annonce (
    id              SERIAL PRIMARY KEY,
    annonce_id      INT  NOT NULL REFERENCES annonces(id) ON DELETE CASCADE,
    jour_semaine    VARCHAR(10) NOT NULL CHECK (
                        jour_semaine IN ('Lundi','Mardi','Mercredi','Jeudi','Vendredi','Samedi','Dimanche')
                    ),
    heure_debut     TIME NOT NULL,
    heure_fin       TIME NOT NULL,
    CHECK (heure_fin > heure_debut)
);


-- ============================================================
-- 4. MATCHING MENTOR / MENTORÉ
-- ============================================================

CREATE TABLE matchings (
    id                  SERIAL PRIMARY KEY,
    mentor_id           INT  NOT NULL REFERENCES utilisateurs(id) ON DELETE CASCADE,
    mentore_id          INT  NOT NULL REFERENCES utilisateurs(id) ON DELETE CASCADE,
    score_compatibilite NUMERIC(5,2),               -- score calculé par l'algorithme (0-100)
    statut              VARCHAR(20) NOT NULL DEFAULT 'propose'
                            CHECK (statut IN ('propose','accepte','refuse','termine')),
    annonce_id          INT  REFERENCES annonces(id) ON DELETE SET NULL,
    date_matching       TIMESTAMP NOT NULL DEFAULT NOW(),
    date_maj            TIMESTAMP NOT NULL DEFAULT NOW(),
    CHECK (mentor_id <> mentore_id),
    UNIQUE (mentor_id, mentore_id, annonce_id)
);


-- ============================================================
-- 5. MESSAGERIE INSTANTANÉE
-- ============================================================

CREATE TABLE conversations (
    id              SERIAL PRIMARY KEY,
    matching_id     INT REFERENCES matchings(id) ON DELETE SET NULL,
    date_creation   TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Participants à une conversation (permet d'étendre à des groupes si besoin)
CREATE TABLE participants_conversation (
    id                  SERIAL PRIMARY KEY,
    conversation_id     INT NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    utilisateur_id      INT NOT NULL REFERENCES utilisateurs(id)  ON DELETE CASCADE,
    date_rejoins        TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE (conversation_id, utilisateur_id)
);

CREATE TABLE messages (
    id              SERIAL PRIMARY KEY,
    conversation_id INT  NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    expediteur_id   INT  NOT NULL REFERENCES utilisateurs(id)  ON DELETE CASCADE,
    contenu         TEXT NOT NULL,
    est_lu          BOOLEAN   NOT NULL DEFAULT FALSE,
    date_envoi      TIMESTAMP NOT NULL DEFAULT NOW()
);


-- ============================================================
-- 6. INDEX (performances)
-- ============================================================

CREATE INDEX idx_utilisateurs_email     ON utilisateurs(email);
CREATE INDEX idx_utilisateurs_telephone ON utilisateurs(telephone);
CREATE INDEX idx_annonces_type          ON annonces(type_annonce);
CREATE INDEX idx_annonces_matiere       ON annonces(matiere_id);
CREATE INDEX idx_matchings_mentor       ON matchings(mentor_id);
CREATE INDEX idx_matchings_mentore      ON matchings(mentore_id);
CREATE INDEX idx_messages_conversation  ON messages(conversation_id);
CREATE INDEX idx_messages_date          ON messages(date_envoi);


-- ============================================================
-- 7. DONNÉES INITIALES (filières et quelques matières)
-- ============================================================

INSERT INTO filieres (code, libelle) VALUES
    ('IA',     'Intelligence Artificielle'),
    ('IM',     'Ingénierie Multimédia'),
    ('GL',     'Génie Logiciel'),
    ('SE_IOT', 'Systèmes Embarqués & IoT'),
    ('SI',     'Systèmes d''Information');

INSERT INTO matieres (nom) VALUES
    ('Algorithmique'),
    ('Développement Web'),
    ('Bases de données'),
    ('SQL'),
    ('Python'),
    ('Programmation orientée objet'),
    ('Réseaux informatiques'),
    ('Systèmes d''exploitation'),
    ('Mathématiques discrètes'),
    ('Intelligence Artificielle'),
    ('Machine Learning'),
    ('Électronique numérique'),
    ('UML & Modélisation'),
    ('Sécurité informatique'),
    ('Git & DevOps');
