# Copyright (C) 2026 zizanibot
# See LICENSE file for extended copyright information.
# This file is part of UpdateElectedDB project from https://github.com/zizanibot/UpdateElectedDB.

from typing import Any, Dict, List, Optional, Self, Union

from attrs import define
from pathlib import Path

from common.logger import logger
from download.core import read_json


ELECTION = "\u00e9lections g\u00e9n\u00e9rales"


@define
class Elected:
    ref: str
    civ: str
    last_name: str
    first_name: str
    email: str
    departement_num: str
    departement_name: str
    circonscription_num: str
    circonscription_name: str
    circonscription_code: str
    country: str
    group_abv: str
    group_name: str

    @classmethod
    async def from_deputy_json(cls, data: Any, organe_folder: Path) -> Self:
        ref: str = data["acteur"]["uid"]["#text"]
        last_name: str = data["acteur"]["etatCivil"]["ident"]["nom"]
        civ: str = data["acteur"]["etatCivil"]["ident"]["civ"]
        first_name: str = data["acteur"]["etatCivil"]["ident"]["prenom"]
        mandats: List[Any] = data["acteur"]["mandats"]["mandat"]

        elec: Optional[Dict[str, Any]] = None
        group_ref: str = ""
        group_abv: str = ""
        group_name: str = ""
        circonscription_ref: str = ""
        departement_num: str = ""
        departement_name: str = ""
        circonscription_num: str = ""
        circonscription_name: str = ""
        circonscription_code: str = ""
        elec_found: bool = False

        try:
            for mandat in mandats:
                if not elec_found and "election" in mandat:
                    elec = mandat["election"]
                    if elec:
                        if (
                            isinstance(elec["causeMandat"], list)
                            and ELECTION in elec["causeMandat"]
                        ):
                            elec_found = True
                        elif (
                            isinstance(elec["causeMandat"], str)
                            and ELECTION == elec["causeMandat"].lower()
                        ):
                            elec_found = True
                if (
                    not group_ref
                    and "typeOrgane" in mandat
                    and "GP" == mandat["typeOrgane"]
                ):
                    group_ref = mandat["organes"]["organeRef"]
        except:
            logger.error("Couldn't process election for %s", ref)
            raise

        try:
            if elec:
                departement_num = elec["lieu"]["numDepartement"]
                departement_name = elec["lieu"]["departement"]
                circonscription_num = elec["lieu"]["numCirco"]
                circonscription_ref = elec["refCirconscription"]

                if len(circonscription_num) == 1:
                    circonscription_num = "0" + circonscription_num
                circonscription_code = f"{departement_num}{circonscription_num}"

            if circonscription_ref:
                organe_file = organe_folder / f"{circonscription_ref}.json"
                try:
                    circonscription_data = await read_json(organe_file)
                    circonscription_name = circonscription_data["organe"]["libelle"]
                except OSError:
                    logger.warning(
                        "Cannot find the organe file %s for %s",
                        circonscription_ref,
                        ref,
                    )
            else:
                logger.warning("%s does not have any organe reference.", ref)

            if group_ref:
                organe_file = organe_folder / f"{group_ref}.json"
                try:
                    group_data = await read_json(organe_file)
                    group_abv = group_data["organe"]["libelleAbrege"]
                    group_name = group_data["organe"]["libelle"]
                except OSError:
                    logger.warning(
                        "Cannot find the organe file %s for %s", group_ref, ref
                    )
            else:
                logger.warning("%s does not have any organe reference.", ref)
        except:
            logger.error("Couldn't process election information for %s", ref)
            raise

        try:
            adresses: Union[List[Any], Any] = data["acteur"]["adresses"]["adresse"]
            email: str = ""

            if isinstance(adresses, list):
                for adresse in adresses:
                    if adresse["@xsi:type"] == "AdresseMail_Type":
                        email = adresse["valElec"]
            else:
                if adresses["@xsi:type"] == "AdresseMail_Type":
                    email = adresses["valElec"]
        except:
            logger.error("Couldn't process email addresses for %s: %s", ref)
            raise

        return cls(
            ref=ref,
            civ=civ,
            last_name=last_name,
            first_name=first_name,
            email=email,
            departement_num=departement_num,
            departement_name=departement_name,
            circonscription_num=circonscription_num,
            circonscription_name=circonscription_name,
            circonscription_code=circonscription_code,
            country="France",
            group_abv=group_abv,
            group_name=group_name,
        )

    @classmethod
    async def from_senat(cls, data: Any) -> Self:
        ref: str = data["senmat"]
        last_name: str = data["sennomuse"]
        civ: str = data["quacod"]
        first_name: str = data["senprenomuse"]

        group_abv: str = data["grppolcod"]
        group_name: str = data["grppollilcou"]
        departement_num: str = data["dptcod"]
        departement_name: str = data["dptlib"]
        circonscription_num: str = ""
        circonscription_name: str = ""
        circonscription_code: str = ""
        email: str = data["senema"]

        return cls(
            ref=ref,
            civ=civ,
            last_name=last_name,
            first_name=first_name,
            email=email,
            departement_num=departement_num,
            departement_name=departement_name,
            circonscription_num=circonscription_num,
            circonscription_name=circonscription_name,
            circonscription_code=circonscription_code,
            country="France",
            group_abv=group_abv,
            group_name=group_name,
        )

    @classmethod
    async def from_europarl_csv(cls, data: Any) -> Self:
        ref: str = data["mep_identifier"]
        last_name: str = data["mep_family_name"]
        civ: str = data["mep_honorific_prefix"]
        first_name: str = data["mep_given_name"]

        group_abv: str = ""
        group_name: str = data["mep_political_group"]
        departement_num: str = ""
        departement_name: str = ""
        circonscription_num: str = ""
        circonscription_name: str = ""
        circonscription_code: str = ""
        country: str = data["mep_country_of_representation"]
        email: str = data["mep_email"]

        return cls(
            ref=ref,
            civ=civ,
            last_name=last_name,
            first_name=first_name,
            email=email,
            departement_num=departement_num,
            departement_name=departement_name,
            circonscription_num=circonscription_num,
            circonscription_name=circonscription_name,
            circonscription_code=circonscription_code,
            country=country,
            group_abv=group_abv,
            group_name=group_name,
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ref": self.ref,
            "civ": self.civ,
            "last_name": self.last_name,
            "first_name": self.first_name,
            "email": self.email,
            "departement_num": self.departement_num,
            "departement_name": self.departement_name,
            "circonscription_num": self.circonscription_num,
            "circonscription_name": self.circonscription_name,
            "circonscription_code": self.circonscription_code,
            "country": self.country,
            "group_abv": self.group_abv,
            "group_name": self.group_name,
        }
