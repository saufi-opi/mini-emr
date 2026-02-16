import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import select

from app.core.config import settings
from app.modules.diagnoses.models import Diagnosis
from app.modules.diagnoses.service import get_diagnosis_by_code

ICD10_CODES = [
    {"code": "A00.0", "description": "Cholera due to Vibrio cholerae 01, biovar cholerae"},
    {"code": "A00.1", "description": "Cholera due to Vibrio cholerae 01, biovar eltor"},
    {"code": "A00.9", "description": "Cholera, unspecified"},
    {"code": "A01.00", "description": "Typhoid fever, unspecified"},
    {"code": "A01.01", "description": "Typhoid meningitis"},
    {"code": "A01.02", "description": "Typhoid fever with heart involvement"},
    {"code": "A01.03", "description": "Typhoid pneumonia"},
    {"code": "A01.04", "description": "Typhoid arthritis"},
    {"code": "A01.05", "description": "Typhoid osteomyelitis"},
    {"code": "A01.09", "description": "Typhoid fever with other complications"},
    {"code": "A02.0", "description": "Salmonella enteritis"},
    {"code": "A02.1", "description": "Salmonella sepsis"},
    {"code": "A02.20", "description": "Localized salmonella infection, unspecified"},
    {"code": "A02.21", "description": "Salmonella meningitis"},
    {"code": "A02.22", "description": "Salmonella pneumonia"},
    {"code": "A02.23", "description": "Salmonella arthritis"},
    {"code": "A02.24", "description": "Salmonella osteomyelitis"},
    {"code": "A02.25", "description": "Salmonella pyelonephritis"},
    {"code": "A02.29", "description": "Salmonella with other localized infection"},
    {"code": "A02.8", "description": "Other specified salmonella infections"},
    {"code": "A02.9", "description": "Salmonella infection, unspecified"},
    {"code": "A03.0", "description": "Shigellosis due to Shigella dysenteriae"},
    {"code": "A03.1", "description": "Shigellosis due to Shigella flexneri"},
    {"code": "A03.2", "description": "Shigellosis due to Shigella boydii"},
    {"code": "A03.3", "description": "Shigellosis due to Shigella sonnei"},
    {"code": "A03.8", "description": "Other shigellosis"},
    {"code": "A03.9", "description": "Shigellosis, unspecified"},
    {"code": "A04.0", "description": "Enteropathogenic Escherichia coli infection"},
    {"code": "A04.1", "description": "Enterotoxigenic Escherichia coli infection"},
    {"code": "A04.2", "description": "Enteroinvasive Escherichia coli infection"},
    {"code": "A04.3", "description": "Enterohemorrhagic Escherichia coli infection"},
    {"code": "A04.4", "description": "Other intestinal Escherichia coli infections"},
    {"code": "A04.5", "description": "Campylobacter enteritis"},
    {"code": "A04.6", "description": "Enteritis due to Yersinia enterocolitica"},
    {"code": "A04.71", "description": "Enterocolitis due to Clostridium difficile, recurrent"},
    {"code": "A04.72", "description": "Enterocolitis due to Clostridium difficile, not specified as recurrent"},
    {"code": "A04.8", "description": "Other specified bacterial intestinal infections"},
    {"code": "A04.9", "description": "Bacterial intestinal infection, unspecified"},
    {"code": "A05.0", "description": "Foodborne staphylococcal intoxication"},
    {"code": "A05.1", "description": "Botulism food poisoning"},
    {"code": "A05.2", "description": "Foodborne Clostridium perfringens [Clostridium welchii] intoxication"},
    {"code": "A05.3", "description": "Foodborne Vibrio parahaemolyticus intoxication"},
    {"code": "A05.4", "description": "Foodborne Bacillus cereus intoxication"},
    {"code": "A05.5", "description": "Foodborne Vibrio vulnificus intoxication"},
    {"code": "A05.8", "description": "Other specified bacterial foodborne intoxications"},
    {"code": "A05.9", "description": "Bacterial foodborne intoxication, unspecified"},
    {"code": "A06.0", "description": "Acute amebic dysentery"},
    {"code": "A06.1", "description": "Chronic intestinal amebiasis"},
    {"code": "A06.2", "description": "Amebic nondysenteric colitis"},
    {"code": "A06.3", "description": "Ameboma of intestine"},
    {"code": "A06.4", "description": "Amebic liver abscess"},
    {"code": "A06.5", "description": "Amebic lung abscess"},
    {"code": "A06.6", "description": "Amebic brain abscess"},
    {"code": "A06.7", "description": "Cutaneous amebiasis"},
    {"code": "A06.81", "description": "Amebic cystitis"},
    {"code": "A06.82", "description": "Amebic urethritis"},
    {"code": "A06.89", "description": "Other amebic infections"},
    {"code": "A06.9", "description": "Amebiasis, unspecified"},
    {"code": "A07.0", "description": "Balantidiasis"},
    {"code": "A07.1", "description": "Giardiasis [lambliasis]"},
    {"code": "A07.2", "description": "Cryptosporidiosis"},
    {"code": "A07.3", "description": "Isosporiasis"},
    {"code": "A07.4", "description": "Cyclosporiasis"},
    {"code": "A07.8", "description": "Other specified protozoal intestinal diseases"},
    {"code": "A07.9", "description": "Protozoal intestinal disease, unspecified"},
    {"code": "A08.0", "description": "Rotaviral enteritis"},
    {"code": "A08.11", "description": "Acute gastroenteropathy due to Norwalk agent"},
    {"code": "A08.19", "description": "Acute gastroenteropathy due to other small round viruses"},
    {"code": "A08.2", "description": "Adenoviral enteritis"},
    {"code": "A08.31", "description": "Calicivirus enteritis"},
    {"code": "A08.32", "description": "Astrovirus enteritis"},
    {"code": "A08.39", "description": "Other viral enteritis"},
    {"code": "A08.4", "description": "Viral intestinal infection, unspecified"},
    {"code": "A08.8", "description": "Other specified intestinal infections"},
    {"code": "A09", "description": "Infectious gastroenteritis and colitis, unspecified"},
    {"code": "B00.0", "description": "Eczema herpeticum"},
    {"code": "B00.1", "description": "Herpesviral vesicular dermatitis"},
    {"code": "B00.2", "description": "Herpesviral gingivostomatitis and pharyngotonsillitis"},
    {"code": "B00.3", "description": "Herpesviral meningitis"},
    {"code": "B00.4", "description": "Herpesviral encephalitis"},
    {"code": "B00.50", "description": "Herpesviral ocular disease, unspecified"},
    {"code": "B00.51", "description": "Herpesviral iridocyclitis"},
    {"code": "B00.52", "description": "Herpesviral keratitis"},
    {"code": "B00.53", "description": "Herpesviral conjunctivitis"},
    {"code": "B00.59", "description": "Other herpesviral ocular disease"},
    {"code": "B00.7", "description": "Disseminated herpesviral disease"},
    {"code": "B00.81", "description": "Herpesviral whitlow"},
    {"code": "B00.82", "description": "Herpesviral whitlow"},
    {"code": "B00.89", "description": "Other herpesviral infections"},
    {"code": "B00.9", "description": "Herpesviral infection, unspecified"},
    {"code": "B01.0", "description": "Varicella meningitis"},
    {"code": "B01.11", "description": "Varicella encephalitis"},
    {"code": "B01.12", "description": "Varicella myelitis"},
    {"code": "B01.2", "description": "Varicella pneumonia"},
    {"code": "B01.81", "description": "Varicella keratitis"},
    {"code": "B01.89", "description": "Varicella with other complications"},
    {"code": "B01.9", "description": "Varicella without complication"},
    {"code": "B02.0", "description": "Zoster encephalitis"},
    {"code": "B02.1", "description": "Zoster meningitis"},
    {"code": "B02.21", "description": "Postherpetic geniculate ganglionitis"},
    {"code": "B02.22", "description": "Postherpetic trigeminal neuralgia"},
    {"code": "B02.23", "description": "Postherpetic polyneuropathy"},
    {"code": "B02.24", "description": "Postherpetic myelitis"},
    {"code": "B02.29", "description": "Other postherpetic neurological complication"},
]

async def seed():
    engine = create_async_engine(str(settings.SQLALCHEMY_DATABASE_URI))
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False) # type: ignore
    
    async with async_session() as session:
        # Fetch all existing diagnosis codes to avoid multiple DB calls
        statement = select(Diagnosis.code)
        result = await session.exec(statement)
        existing_codes = set(result.all())

        to_insert = []
        for item in ICD10_CODES:
            if item["code"] not in existing_codes:
                to_insert.append(Diagnosis(**item))
        
        if to_insert:
            session.add_all(to_insert)
            await session.commit()
            print(f"Successfully seeded {len(to_insert)} new diagnoses.")
        else:
            print("No new diagnoses to seed.")

    print("Seeding process completed!")

if __name__ == "__main__":
    asyncio.run(seed())
