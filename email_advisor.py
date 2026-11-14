def generate_bilal_cold_email(prof_name: str, institution: str, topic: str, lang: str = "en") -> str:
    """
    توليد بريد إلكتروني مخصص بنسبة 100% للمهندس بلال حداد يبرز نقاط القوة الخارقة في سيرته:
    • ماستر غوبكين للغاز والمكثفات + ماستر جامعة كاتانيا بإيطاليا (نظام ECTS)
    • خبرة ميدانية نوعية في شراكة سوناطراك وإيني (Association GSE) وحقل عين صالح
    • نمذجة تدفق الموائع متعددة الأطوار وهندسة المكامن
    """
    if lang == "it":
        return f"""
Gentile Prof. {prof_name},

Le scrivo per manifestare il mio forte interesse per le attività di ricerca del Suo gruppo presso {institution}, con particolare riferimento all'ambito di {topic}.

Sono un ingegnere della produzione e giacimenti di gas (Laurea Magistrale conseguita presso la Gubkin Russian State University of Oil and Gas a Mosca con votazione 4.6/5.0) e attualmente sto completando un secondo percorso di Laurea Magistrale presso l'Università di Catania (sistema ECTS europeo). 

Sul piano professionale, ho maturato esperienza diretta sul campo in Algeria, in particolare presso la joint venture Association GSE (SONATRACH–Eni) e nel giacimento di In Salah (SONATRACH), lavorando sull'analisi del comportamento di produzione dei pozzi di gas e sulla modellazione di flussi multifase (modelli di Turner e Lea).

Sarei estremamente onorato di poter svolgere la mia tesi di laurea magistrale o candidarmi per una posizione di Dottorato di Ricerca (Ph.D. / borsa PNRR / borsa Eni) sotto la Sua supervisione. Data la mia regolare iscrizione universitaria in Italia, non è richiesta alcuna procedura di equivalenza o visto aggiuntivo per l'avvio immediato dell'attività.

In allegato Le trasmetto il mio Curriculum Vitae dettagliato. Resto a Sua completa disposizione per un breve colloquio conoscitivo, anche online.

Cordiali saluti,
Bilal Haddad
M.Sc. Candidate | University of Catania (Italy)
Ex M.Sc. Gubkin University | Petroleum Production & Gas Engineer
Telefono: +39 351 322 6758 | Email: bilalhaddadeng@gmail.com
LinkedIn: linkedin.com/in/haddadbilal
""".strip()
    elif lang == "fr":
        return f"""
Monsieur le Professeur {prof_name},

Actuellement étudiant en Master à l'Université de Catane en Italie, et titulaire d'un premier Master spécialisé en exploitation des puits de gaz et de condensat de l'Université d'État Gubkin du Pétrole et du Gaz de Moscou (mention 4.6/5.0), je me permets de vous contacter afin de vous soumettre ma candidature pour une thèse de doctorat ou un stage de recherche au sein de {institution}, sur la thématique de {topic}.

Mon parcours combine une formation technique de pointe et une solide expérience opérationnelle sur le terrain en Algérie, notamment au sein de l'Association GSE (joint-venture SONATRACH–Eni) et sur le champ gazier d'In Salah. Mon travail de recherche a porté sur la modélisation des écoulements multiphasiques et l'optimisation de la production des puits de gaz.

Vos projets de recherche correspondent parfaitement à mon expertise en dynamique des réservoirs et écoulements en milieux poreux. Étant déjà inscrit dans le système universitaire italien (crédits ECTS européens), mon intégration académique et administrative est immédiate.

Vous trouverez ci-joint mon Curriculum Vitae détaillé. Je reste à votre entière disposition pour un échange en visioconférence.

Veuillez agréer, Monsieur le Professeur, l'expression de mes salutations les plus distinguées.

Bilal Haddad
Ingénieur Production Pétrolière & Gaz | M.Sc. Université de Catane
Tél : +39 351 322 6758 | Email : bilalhaddadeng@gmail.com
LinkedIn : linkedin.com/in/haddadbilal
""".strip()
    else: # English
        return f"""
Subject: Prospective PhD / Research Opportunity: Inquiry regarding {topic} - Bilal Haddad

Dear Professor {prof_name},

I hope this email finds you well.

My name is Bilal Haddad, and I am writing to express my strong interest in joining your research group at {institution} as a PhD candidate or research intern focusing on {topic}.

I hold an M.Sc. in the Design and Exploitation of Gas and Gas Condensate Wells from Gubkin Russian State University of Oil and Gas in Moscow (GPA: 4.6/5.0), where my thesis focused on multiphase flow modeling and liquid loading prediction in gas wells (In Salah Field, Algeria). Currently, I am completing a second Master's degree at the University of Catania in Italy (European ECTS framework).

Complementing my academic background, I have gained hands-on operational field experience in Algeria, including work with Association GSE (SONATRACH–Eni Joint Venture) and SONATRACH (In Salah Field), focusing on production troubleshooting and well performance optimization. 

Having followed your group's publications in reservoir engineering, multiphase fluid flow in porous media, and subsurface energy systems, I would be privileged to contribute to your ongoing research projects. Because I am currently based in Italy within the European university framework, I am eligible for immediate enrollment and funding frameworks without credential recognition delays.

I have attached my Curriculum Vitae for your review. Thank you very much for your time and consideration, and I welcome the opportunity to discuss any potential openings at your convenience.

Sincerely,
Bilal Haddad
Petroleum Production & Gas Engineer | M.Sc. Candidate, University of Catania (Italy)
Phone: +39 351 322 6758 | Email: bilalhaddadeng@gmail.com
LinkedIn: linkedin.com/in/haddadbilal
""".strip()
