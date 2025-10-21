# -*- coding: utf-8 -*-

"""
Module principal pour la bibliothèque de facturation électronique.

Ce module expose les classes et fonctions les plus importantes de la bibliothèque
pour une utilisation simplifiée, en se concentrant sur l'API moderne et intuitive.

L'usage recommandé est d'instancier un modèle `FactureFacturX` puis d'utiliser
la méthode `.generer_facturx(profil)` pour démarrer le processus de construction.
"""

from .api.chorus_pro import ChorusProAPI
from .api.pannylane import PennylaneAPI
from .api.sage import SAGEAPI

from .afnor_client.client import (
    FlowServiceClient,
    DirectoryServiceClient,
    AFNORAuthError,
    AFNORAPIError,
)

from .models import (
    AdresseElectronique,
    AdressePostale,
    CadreDeFacturation,
    CategorieTVA,
    CodeCadreFacturation,
    CodeRaisonReduction,
    Destinataire,
    FactureBase,
    FactureChorus,
    FactureFacturX,  # Point d'entrée principal pour la nouvelle API !
    Fournisseur,
    LigneDePoste,
    LigneDeTVA,
    ModeDepot,
    ModePaiement,
    MontantTotal,
    PieceJointeComplementaire,
    PieceJointePrincipale,
    References,
    SchemeID,
    TypeFacture,
    TypeTVA,
)

from .exceptions import (
    XSLTValidationError,
    ErreurConfiguration,
    InvalidDataFacturxError,
)

from .utils.facturx import ProfilFacturX


__all__ = [
    # Clients API
    "ChorusProAPI",
    "PennylaneAPI",
    "SAGEAPI",
    "FlowServiceClient",
    "DirectoryServiceClient",
    # Modèles de Données
    "AdressePostale",
    "AdresseElectronique",
    "CadreDeFacturation",
    "CategorieTVA",
    "CodeCadreFacturation",
    "CodeRaisonReduction",
    "Destinataire",
    "FactureBase",
    "FactureChorus",
    "FactureFacturX",
    "Fournisseur",
    "LigneDePoste",
    "LigneDeTVA",
    "ModeDepot",
    "ModePaiement",
    "MontantTotal",
    "PieceJointeComplementaire",
    "PieceJointePrincipale",
    "References",
    "SchemeID",
    "TypeFacture",
    "TypeTVA",
    # Exceptions
    "XSLTValidationError",
    "ErreurConfiguration",
    "InvalidDataFacturxError",
    "AFNORAuthError",
    "AFNORAPIError",
    # Nouvelle API Factur-X
    "ProfilFacturX",
]
