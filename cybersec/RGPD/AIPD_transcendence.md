2 PIA
	- adresse courriel pour inscription
	- donnees api42 pour personnalisation profil (photo profil, banniere+couleur de coalition, 42 UID)



# Analyse d'Impact relative a la Protection des Donnees / Privacy Impact Assessment


objectifs
	description detaille du traitment des donnees
	evaluation conformite rgpd
	identification des risques pour les droits/libertes des personnes concernees
	(au besoin) traitement de ces risques pour les reduire a un niveau acceptable





traitement de donnees pour inscription au site


## Contexte
	collecter l'adresse courriel pour permettre l'inscription par envoi d'un lien, afin de confirmer qu'il s'agit bien d'une personne physique
	une fois l'inscription effectuee, les modifications d'elements sensibles (mot de passe, adresse courriel) sont validee par l'envoi d'un lien sur l'adresse courriel afin de limiter le piratage de compte

## Principes fondamentaux
	finalites: securisation de l'inscription et des modifications du compte
	fondement: 
		liceite: la personne donne librement son adresse, le courriel de confirmation inscription dira clairement que l'adresse courriel sera uniquement a fin d'inscription et modif compte
	minimisation: pas d'autre donnee de confirmation d'identite, il ne s'agit ps de verifier qui est la personne elle-meme, mais juste qu'il s'agit de celle qui a ouvert le compte
	qualite des donnees: la personne a toute latitude de modifier son adresse courriel de contact.
	duree de conservation: jusqu'a suppression du compte car c'est la seule info dispo pour individualiser la possession du compte


mesures protectrices des droits
	- info des personnes via courriel qu'elles peuvent juste ne rien faire si pas de souhait de s'inscrire/modifer donnees compte
	- info dans courriel ET/OU page du site sur droit acces/rectification/suppression/etc
	- quand compte linked with 42 : confirmer que les infos sont juste banniere+couleur de coa et photo de profil



## Risques de securite des donnees
sources de risques
	employes/pirates
quoi
	recuperation illegitime adresse courriel
ou`
	base de donnees
pour
	messages non sollicites

determiner:
	gravite	vraisemblance	-> niveau de risque

mesures existantes/prevues de mitigation des risques

