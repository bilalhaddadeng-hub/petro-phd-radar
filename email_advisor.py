# -*- coding: utf-8 -*-
"""
email_advisor.py
Generates authentic, direct, human academic cold emails for Bilal Haddad.
Written from the perspective of a focused gas/reservoir production engineer,
avoiding generic AI filler clichés ("I hope this email finds you well", "privileged to contribute").
"""

def generate_bilal_cold_email(prof_name: str, institution: str, topic: str, lang: str = "en") -> str:
    # Clean topic and professor name
    p_name = prof_name.replace("Prof. ", "").replace("Professor ", "").strip()
    if not p_name or p_name == "[اسم الأستاذ]":
        p_name = "Professor"

    if lang == "it":
        return f"""
Oggetto: Candidatura Dottorato di Ricerca / Tesi Magistrale - Ingegneria dei Giacimenti e Flussi Multifase

Gentile Prof. {p_name},

Le scrivo direttamente per verificare se nel Suo gruppo di ricerca presso {institution} vi siano posizioni aperte per un Dottorato di Ricerca o un tirocinio per tesi magistrale nell'ambito di {topic}.

Ho conseguito la laurea magistrale in Progettazione e Sfruttamento dei Pozzi di Gas e Condensato presso la Gubkin University di Mosca con votazione 4.6/5.0. Il mio lavoro di tesi si è concentrato sulla modellazione dei flussi multifase (modelli di Turner e Lea) e sul liquid loading applicato ai pozzi del giacimento di In Salah in Algeria. Attualmente sto completando una seconda laurea magistrale in Ingegneria Chimica per la Sostenibilità Industriale presso l'Università di Catania (sistema ECTS).

Sul piano pratico, ho maturato esperienza sul campo in Algeria presso la joint-venture Association GSE (SONATRACH–Eni) e con SONATRACH a In Salah, lavorando su monitoraggio pozzi, troubleshooting di produzione e dinamica di giacimento. 

I progetti del Suo gruppo sulla dinamica dei fluidi in mezzi porosi e lo stoccaggio geologico si collegano direttamente al mio percorso. Trovandomi già regolarmente iscritto in un ateneo italiano, l'avvio amministrativo (borse PNRR, borse industriali o contratti di ricerca) può avvenire immediatamente e senza procedure di equivalenza o visti.

Le allego il mio Curriculum Vitae. Qualora vi fosse una disponibilità, sarei lieto di svolgere un breve colloquio di 10-15 minuti su Teams per approfondire le opportunità.

Un cordiale saluto,

Bilal Haddad
Ingegnere di Produzione Gas & Giacimenti | M.Sc. Università di Catania
Cellulare: +39 351 322 6758 | Email: bilalhaddadeng@gmail.com
LinkedIn: linkedin.com/in/haddadbilal
""".strip()

    elif lang == "fr":
        return f"""
Objet : Candidature Doctorat / Stage de recherche - Ingénierie des réservoirs et écoulements multiphasiques

Bonjour Monsieur le Professeur {p_name},

Je me permets de vous contacter directement afin de savoir si votre équipe au sein de {institution} dispose d'une opportunité de thèse de doctorat ou d'un stage de recherche orienté vers {topic}.

Titulaire d'un premier Master en Exploitation des Puits de Gaz et Condensat de l'Université Gubkin à Moscou (mention 4.6/5.0), mon mémoire a porté sur la modélisation des écoulements multiphasiques (modèles de Turner et Lea) et la prédiction du liquid loading sur le champ gazier d'In Salah en Algérie. Je finalise actuellement un second Master à l'Université de Catane en Italie (cadre européen ECTS).

Sur le plan opérationnel, j'ai effectué plusieurs stages de terrain en Algérie, notamment au sein de l'Association GSE (joint-venture SONATRACH–Eni) et à In Salah, travaillant sur l'analyse de production des puits et la dynamique des réservoirs.

Vos axes de recherche sur les écoulements en milieux poreux et le stockage souterrain (CCUS / H2) correspondent exactement à mon profil technique. Étant déjà inscrit dans une université européenne en Italie, les démarches administratives et contractuelles sont directes et sans délai de visa.

Mon CV est joint à ce message. Si une opportunité est envisageable, je reste disponible pour un bref échange en visioconférence à votre convenance.

Bien cordialement,

Bilal Haddad
Ingénieur Production Pétrolière & Gaz | M.Sc. Université de Catane
Tél : +39 351 322 6758 | Email : bilalhaddadeng@gmail.com
LinkedIn : linkedin.com/in/haddadbilal
""".strip()

    else: # English
        return f"""
Subject: PhD / Research inquiry: Multiphase Reservoir Dynamics & Subsurface Storage - Bilal Haddad

Dear Professor {p_name},

I am writing to inquire if you have an open PhD position or research internship in your group at {institution} for 2026/2027 focusing on {topic}.

By way of background, I hold an M.Sc. in Gas & Condensate Well Exploitation from Gubkin Russian State University in Moscow (GPA 4.6/5.0). My thesis applied Turner and Lea multiphase flow models to predict liquid loading using field operational data from the In Salah gas field in Algeria. I am currently completing a second Master's in Chemical Engineering for Industrial Sustainability at the University of Catania in Italy (European ECTS framework).

In addition to academic modeling, I have practical field experience from technical internships with Association GSE (the SONATRACH–Eni joint venture in Algeria) and SONATRACH at In Salah, working on gas well performance and production troubleshooting.

Your group's focus on multiphase flow in porous media and subsurface energy storage aligns directly with my technical background. Because I am currently enrolled in an Italian university within the EU framework, administrative onboarding and enrollment (via university fellowships, PNRR, or industrial agreements) can proceed smoothly without foreign degree recognition delays.

My CV is attached for your review. If there might be an opening in your lab, I would appreciate the opportunity for a brief 10–15 minute conversation on Teams or Zoom.

Best regards,

Bilal Haddad
Petroleum Production & Gas Engineer | M.Sc. Candidate, University of Catania (Italy)
Phone: +39 351 322 6758 | Email: bilalhaddadeng@gmail.com
LinkedIn: linkedin.com/in/haddadbilal
""".strip()
