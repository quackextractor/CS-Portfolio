# **Decisions made**

**Prompt (C# version)**

Build a **D2 web application** using:

* **Backend**: ASP.NET Core 8 Web API (C#)

* **Frontend**: Vite + React + TypeScript with shadcn-ui

Responsive, mobile-friendly, no emojis

* **Database**: Microsoft SQL Server

Schema requires explicit commits. This decision is final.

* **ORM/Pattern**: Custom **Active Record (D2)** implementation. No EF Core abstractions.

* **Testing**: xUnit + Moq

### Principles

* KISS

* DRY

* ACID compliant transactions

* Strong error handling

### Requirements

* Active Record proof (CRUD + persistence per entity)

* Transaction proof (rollback on failure)

* Import functionality fully working

* Centralized and consistent error handling

* Write tests for **every scenario**, no exceptions

### Domain

Hotel Management System

### Testing Scenarios (deliver as 3 md files)

1. **Setup scenario**

* Installation

* Configuration

* Database setup

2. **Happy path scenario**

* Add, edit, delete entities

* Generate reports

3. **Error scenario**

* Invalid inputs

* Database offline

* Configuration errors

### Documentation (Checklist)

Use placeholders where needed (diagrams, screenshots).

Include:

* ER diagram

* UI screenshots

* Step-by-step setup guide

* Explanation of the custom Active Record implementation

* Known issues and limitations

Follow the provided assignment checklist exactly.

# Clarifications

### ✅ **Clarified Approach:**

1. **Database**: Use **Microsoft SQL Server** as per the prompt. The school has a local instance accessed like so:
```
# Database Configuration  
DB_CONNECTION_STRING="DRIVER={ODBC Driver 17 for SQL Server};SERVER=193.85.203.188;DATABASE=schoolusername;UID=schoolusername;PWD=password;TrustServerCertificate=yes"

# Alternative: local instance  
# DB_CONNECTION_STRING="DRIVER={ODBC Driver 17 for SQL Server};SERVER=(localdb)localDB1;Trusted_Connection=yes;TrustServerCertificate=yes"  
# DB_CONNECTION_STRING="DRIVER={ODBC Driver 17 for SQL Server};SERVER=PCXXXX;DATABASE=ChronoLog;UID=schoolusername;PWD=schoolpassword;TrustServerCertificate=yes"  
```
2. **Active Record**: Keep it **KISS** – per-entity CRUD, base class with `Save()`, `Delete()`, `Find()`, `Where()`. Transaction support will be explicit.  
3. **Testing**: We'll write:  
   - **3x test scenarios in Markdown** (PDF-ready)  
   - **xUnit + Moq unit tests** for all business logic, repositories, and services  
4. **Import**: Web UI with file upload → parse CSV/JSON → validate → insert into relevant tables.  
5. **UI/UX**: Guided workflows for non-technical users (e.g., “Book a Room” wizard).

# **Projekt s RDBMS**

Požadavky na absolvování

Cílem je přidat přímo do Vašeho portfolia aplikaci s **uživatelským rozhraním** nebo API, která využívá relační **databázi**.Může být pro libovolnou činnost nebo agendu. Musí ale obsahovat **jednu** z následujících skupin zadání D1 až D3 dle vlastního výběru:

**D1** Řešení musí využívat Vámi vytvořený buď DAO, TableGateway nebo Repository pattern  
**D2** Řešení musí využívat Vámi vytvořený buď Row gateway nebo Active record pattern  
**D3** Řešení musí využívat Vámi vytvořený Object-relation mapping (Mapper pattern)

Doporučujeme si zvolit takovou databázi (RDBMS), která je ve škole nainstalovaná, nebo se na ní lze ze školního PC alespoň připojit.

Kromě výše uvedeného musí Vaše řešení splnit následující požadavky:

Musíte použít skutečný relační databázový systém (případně objektově-relační, nelze ale použít jiné typy databází nebo SQLite)

1. Aplikace musí pracovat s databází, která obsahuje minimálně: 5x tabulek (včetně vazebních), 2x pohled (view), 1x vazba M:N  
2. Mezi atributy tabulek musí být minimálně 1x zastoupen každý z datových typů: Reálné číslo (float), Logická hodnota (bool nebo ekvivalent), Výčet (enum), Řetězec (string, varchar), Datum nebo čas (datetime, date, time).  
3. Musíte umožnit vložení, smazání, zobrazení a úpravu nějaké informace, která se ukládá do více než jedné tabulky. Například vložení objednávky, která se na úrovni databáze rozloží do tabulek objednavka, zakaznik a polozky  
4. Do aplikace naprogramovat mininálně jedno použití transakce nad více než jednou tabulkou. Například převod kreditních bodů mezi dvěma účty apod.  
5. Pomocí aplikace generovat souhrnný report, který bude obsahovat smysluplná agregovaná data z alespoň tří tabulek. Např. různé počty položek, součty, minima a maxima, apod.  
6. Umožnit import dat do min. dvou tabulek z formátu CSV, XML nebo JSON.  
7. Umožnit nastavovat program v konfiguračním souboru.  
8. Ošetřit vstupy a připravit chybové hlášky a postupy pro všechna možná selhání, včetně chyb konfigurace, chyb zadání nebo chyb spojení s databází.

Kromě zdrojového kódu k programu musíte zpracovat také min. 3x testovací scénář a 1x dokumentaci:

* 1x [Testovací scénář](https://moodle.spsejecna.cz/mod/resource/view.php?id=2116) ve formátu PDF (.pdf) pro spuštění aplikace, včetně nastavení a importu databázové struktury.

* min. 2x [Testovací scénáře](https://moodle.spsejecna.cz/mod/resource/view.php?id=2116) ve formátu PDF (.pdf) podle kterých můžeme otestovat všechny výše uvedené body, včetně všech druhů chyb a možností konfigurace. V případě všech možných chyb musí program rozumným způsobem reagovat, nebo vyžadovat součinnost uživatele k vyřešení problému. To je třeba podchytit v testovacích scénářích.

* 1x dokumentaci, která bude obsahovat vše z [Příloha 1 - Checklist](https://moodle.spsejecna.cz/mod/resource/view.php?id=2077) v českém nebo anglickém jazyce.

Bez splnění hlavního úkolu **D1-D3** výše nebo nedodání **min. 3 testovacích scénářů** bude práce hodnocena známkou 5 - nedostatečný i přesto, že jinak bude funkční a třeba i dobře zpracovaná. V případě vynechání jednoho z bodů 1. až 9. bude známka snížena o dva stupně, tj. vynechání tří a více bodů povede ke známce 5 - nedostatečný. Dejte pozor na plagiáty a cizí kód, který když využijete je třeba uvést původního autora, zejména u knihoven a dalších balíčků.

### **Testování**

Vaše programy podle odkazů na Vámi dříve odevzdaná portfolia stáhneme na školním PC.tentokrát Pokud budete chtít odkaz na portfolio upravit, rychle nás kontaktujte. Vaše řešení může, ale nemusí obsahovat unit testy, na místo toho musí obsahovat testovací scénáře pro testery.

Tester bude člověk, který bude aplikaci na školním PC testovat a nebudete to Vy. Testování může provádět jiný žák naší školy, externí tester nebo další přizvané osoby. Vaše práce tak bude hodnocena nejen učitelem ale i testerem právě dle scénářů a dokumentace. Nejprve hodnotí tester a jen a pouze pokud budou testování dopadne uspokojivě, bude nahlíženo učitelem i do zdrojového kódu v rámci běžných kontrol portfolia.

Ve vašem portfoliu tedy připravte **a jasně označte která aplikace, nebo který projekt splňuje toto zadání pomoci označení D1, D2 nebo D3.** Nezapomeňte, že tester bude Vaší aplikaci stahovat z gitu a instalovat. Potřebuje k tomu tedy nejen zdrojové kódy, ale SQL DDL, postup vytvoření a konfigurace databázových účtů a konfigurace připojení apod. Projekt je dobré rozdělit do adresářů, například zdrojový kód do složky /src, dokumentaci do složky /doc a testy do složky /test, nebo jiným vhodným způsobem.

Při odevzdání platí následující pravidla:

* Vaši práci musíte učiteli podrobně vysvětlit, odpovídat na případné dotazy a **to jen s použitím** **Vašeho zdrojového kódu a Váši dokumentace**.  
* Váš program musí být spustitelný i bez použití IDE podle návodu na instalaci, například README nebo jiné dokumentace. Pozor na to, že práce potřebuje i import databáze.  
* Prezentace musí proběhnout na školním PC, **nelze odevzdávat na Vašem notebooku.** Je ale možné se ze školního PC připojit pomocí sítě (např. internet) na Vaše servery, či jiná zařízení a nebo spouštět webové stránky, atd.

### **FAQ**

**Mohu použít SQLite?** Ne, to není relační databáze v klasickém smyslu.

**Jaký mám použít databázový server?** Můžete využít ty, které jsou na školním PC nainstalované a k nim udělat návod pro import, nebo jakýkoliv běžící server na internetu, ale pozor abyste tím neprozradili své přihlašovací údaje. Projekty budou sdíleny mezi ostatní žáky, včetně zdrojového kódu.

**Lze odevzdat práci bez hlavního úkolu?** Ne.

**Lze odevzdat práci bez testovacích scénářů?** Ne.

**Opravdu nemohu odevzdat na svém notebooku?** Ne.

**Jaké jsou požadavky pro implementaci enumu v DB systémech, které tento dat. typ nenabízejí?** Například pomocí CHECK constraint. V MSSQL by to mohlo být např.: `odpoved VARCHAR(5) NOT NULL CHECK (odpoved IN('ano', 'ne', 'možná'))`  
   
**Jak by měla vypadat realizace bodu 4?** Například si to lze představit pomocí formuláře pro objednávku v klasickém nákupním košíku. Jde o to, že z hlediska UI je to jeden formulář objednávky s jedním tlačítkem odeslat. Data ale uloží do mnoha tabulek. ~~Špatně by bylo, kdyby ke každé tabulce v databázi existoval právě jeden formulář a například u objednávky, by uživatel nejprve zadal její položky, pak své údaje, pak objednávku a nakonec ještě musel vložit data do vazebních tabulek.... tfuj, radši to šrktnu.~~  
   
**Mohu vytvořit pouze API bez uživatelského rozhraní?** Ne. Vytvořit API je správně, ale je třeba k němu doprogramovat/nastavit také uživatelské rozhraní, které ho používá. Jako uživatelské rozhraní můžete ale využít již nějaké existující, které lze na školním PC provozovat. Například rozhraní chatu discord, pokud děláte chatbota apod. Nelze ale odevzdat jen knihovnu funkcí, nebo službu například jen s REST API, apod. Aplikace musí být použitelná pro běžného uživatele bez technického vhledu, např. Vaše rodiče.  
   
**Mohu použít dapper, alchemy, entity framework nebo hotové ORM?** Ne. Musíte vytvořit vlastní - o tom je tato úloha.

# **Jak zpracovat dokumentaci?**

Požadavky na absolvování

*Každý program, software nebo aplikace je z dlouhodobého hlediska jen tak kvalitní, jak kvalitně má zpracovanou dokumentaci. Projekty bez dokumentace nelze v tomto předmětu brát vážně, leda by k tomu byl nějaký důvod.*

Proto při zpracování dokuemntace myslete na níže uvedené body a držte se jich:

* Dokumentace obsahuje **název projektu**, jméno autora, jeho kontaktní údaje, datum vypracování, název školy a informaci, že se jedná o školní projekt.  
* Dokumentace obsahuje nebo odkazuje na **specifikaci požadavků** uživatele/zadavatele na práci s aplikací, nebo na UML Use Case diagramy, které toto popisují. Vhodnou formou jsou například business requirements nebo functional requirements.  
* Dokumentace obsahuje **popis architektury** aplikace. To lze popsat pomocí návrhových vzorů, nebo UML strukturálních diagramů (např. Class diagramy, Deployment diagramy apod.), nebo alespoň schématickým „big image“ shrnujícím celou aplikaci, její komponenty/části a vazby mezi nimi.  
* Dokumentace obsahuje **popis běhu aplikace** pomocí UML behaviorálních diagramů (např. State diagramy, Activity diagramy apod.). Tedy nejen statický popis toho, jaké má komponenty a jaké mají vazby, ale i jak funguje běh aplikace v typických případech.  
* Dokumentace obsahuje, nebo odkazuje **použitá rozhraní, protokoly a specifikace** všech subsystémů a knihoven třetích stran, na kterých je jakkoli závislá. Vhodnou formou jsou například non-functional requirements. Vždy se uvádí výčet knihoven třetích stran, které program využívá, či služeb, na kterých je silně závislý.  
* Dokumentace obsahuje informace o **právních a licenčních aspektech** projektu, případně o dalších autorskoprávních omezeních souvisejících s provozem aplikace.  
* Dokumentace obsahuje informace o **konfiguraci** programu. Jak se program konfiguruje, jaké konfigurační volby jsou přípustné a co dělají.  
* Dokumentace obsahuje popis **instalace a spuštění** aplikace, případně odkazuje na soubor README.txt, kde je tento postup popsán.  
* Dokumentace obsahuje popis všech **chybových stavů**, které mohou v aplikaci nastat, případně i kódy chyb a postup jejich řešení.  
* Dokumentace obsahuje informace o **způsobu ověření, testování a validace** aplikace, včetně popisu provedených testů, jejich výsledků a zhodnocení, zda aplikace splňuje stanovené požadavky.  
* Dokumentace obsahuje, nebo odkazuje **seznam verzí a známých bugů** či issues.  
* **Pokud** aplikace používá databázi, obsahuje E-R model databáze, ze kterého jsou patrné názvy tabulek, atributů, jejich datové typy a další konfigurační volby, pokud aplikace databázi používá.  
* **Pokud** aplikace používá síť, tak musí obsahovat schéma sítě, rozsahy a její konfiguraci.  
* **Pokud** aplikace využíví nějaké jiné služby, HW, nebo SQ, např. webový server, musí obsahovat jeho kompletní nezbytnou konfiguraci. Musí obsahovat vše, co je ke konfiguraci a běhu nezbytné.  
* **Pokud** aplikace umožňuje import/export, obsahuje schéma importovaných a exportovaných souborů, včetně povinných a nepovinných položek a pravidel pro import/export.  
* Dokumentace je zpracována **v jednom souboru** s příponou .**pdf** nebo .**md**, **nebo jako HTML stránka** se vstupním souborem index.**htm**.

# **Jak zpracovat programátorský projekt nebo jeho část?**

Požadavky na absolvování

*Každý projekt musí mít dobrou vnitřní strukturu a vlastní pravidla, která dodržuje. Není fixně dáno, jak má struktura a pravidla vypadat, protože různé projekty mají svá specifika a například kvůli použití frameworku. Je ale zlatým pravidlem, že všechny části projektu, které tvoříte, dodržují stejné principy, pravidla a drží se stejné struktury. Vyjímku mají jen knihovny třetích stran, kde tato pravidla i tak uplatníme - na to, jak je používáme.*

**Stanovujeme ale následující zásady, které je třeba dodržet a to i za cenu toho, že projekt, framework, či zvyklost budete muset pro tento školní projekt porušit:**

* Projekt musí být z větší části softwarový a musí mít smysluplné reálné použití.  
* Projekt musí být verzovaný, nejlépe pomocí git.   
* U každé části projektu musí být zřejmé, kdo je jejím autorem. U zdrojových kódů, stejně jako u SQL či jiných skriptů a dokonce i u obrázků a grafiky.  
* Pokud projekt používá databázi, musí obsahovat skripty pro její vytvoření. U relační databáze DDL, a případně i DML příkazy v transakcích.  
* Projekt musí mít rozumnou strukturu složek, modulů či jiných komponent. Typicky složky, kde /*src* je pro kód, /*test* pro unit testy, /*doc* pro dokumentaci, */bin* pro spustitelné soubory a skripty, apod.  
* Zdrojové kódy buď obsahují vhodnou dokumentaci, nebo je zdrojový kód dobře čitelný.  
* Projekt musí obsahovat dokumentaci a návod ke spuštění i k provedení základních funkcí. Nejlépe pomocí souboru README.md, nebo jako HTML, či jiný vhodný formát.  
* Projekt musí mít jasně vymezený způsob konfigurace.  
* Projekt musí být spustitelný na jednom, nebo více školních PC v učebně, kde se vyučuje předmět PV, nebo na jiném školním zařízení v jiné učebně po dohodě s vyučujícím a to bez použití IDE.  
* Veškerý zdrojový kód, který není autorský (tj. není vytvořen Vaší vlastní rukou) musí být v samostatné složce, která bude vhodně nazvaná, například */lib*, nebo */vendor*. Nelze tedy do jednoho souboru umístit jak Váš autorský kód, tak i cizí kód. K oddělení cizího kódu musíte tak využít sobory, knihovny, package a volání funkcí, kterými případný cizí kód oddělíte. (Pomocí komentářů, nebo jiného označení to nepostačuje.)

# **Co a jak se bude hodnotit?**

Požadavky na absolvování

Cílem je, abyste získali znalosti, schopnosti a dovednosti v IT. Budete budovat profesionální portfolio, které ukáže vaši iniciativu, samostatnost a schopnost řešit úkoly. Portfolio se hodnotí průběžně, podle toho, co každý týden nového přinesete.

Ukazujete, že umíte pracovat s technologiemi, analyzovat a zlepšovat kód, spolupracovat na cizích projektech a učit se nové věci.

###### **Průběžný rozhovor**

Každý týden nebo dva proběhne krátký osobní rozhovor (cca 5 min) o vašem postupu. Hodnotíme pokrok, iniciativu a plnění úkolů. Pokud chybíte nebo rozhovor nestihneme, budete dohánět intenzivněji další týden.

###### **Úkoly a diferencované hodnocení**

*Každý z vás dostane individuální úkoly. Úkolem je zapisovat si je a prezentovat výsledky.* Porozumění ústním instrukcím je klíčová dovednost. Úkoly mohou být zaměřené na programování, testování, návrhy a dokumentaci. Hodnotíme vaši vlastní práci a schopnosti, ne kopírování kódu.

Každý z vás bude dostávat úkoly přizpůsobené vaší situaci. Každý bude mít jiné úkoly a vaším úkolem je i zapisovat si zadání a obhajovat Vámi navržené řešení. Jen velmi málo informací dostanete přehledně písemně, a proto bude porozumění ústním instrukcím jednou z hlavních dovedností. Někdo se bude více soustředit na programování, někdo na testování, jiný na návrhy a dokumentaci. Cílem je ukázat vlastní práci a schopnosti, ne kopírovat hotový kód.

###### **Používání AI**

AI generátory kódu můžete používat, ale nesete plnou odpovědnost. Nehodnotíme kód, ale vaše znalosti. Musíte rozumět každé části, umět ji opravit nebo změnit. Kód, se kterým neumíte pracovat, *bude mít následky*.

###### **Spolupráce a cizí kód**

Může se stát, že projekt budete muset předat spolužákovi nebo přijmout cizí kód. Hodnotíme vaše porozumění, schopnost opravit a zlepšit kód, nikoli autora kódu.

##### **Co se bude hodnotit? Úplně základní věci, jako například:**

Všechny úkoly musí dodržovat pravidla níže a budou hodnoceny podle toho, jak žák ovládá požadované koncepty a dovednosti. Úkoly musí být srozumitelné a demonstrovat schopnosti získané během studia:

* Configurability and universality – Porozumění a tvorba konfigurace, schopnost upravit a rozšířit konfiguraci různým situacím  
* Architecture and design patterns – Návrh architektury, objektový model a rozhraní, rozpoznání vhodných design patterns a osvědčených řešení problémů.  
* Usability and program control – Schopnost navrhnout ovladatelné rozhraní nebo API, které je přehledné a logické pro uživatele i programátora.  
* Correctness and efficiency – Vyhodnocení, zda program funguje správně,, debugování a odhalování chyb, návrh efektivního řešení se správným využitím zdrojů.  
* Testing and error handling –Testování a ověřování funkčnosti kódu, schopnost odhalit chyby, navrhovat řešení pro různé typy výjimek a unit testy.  
* Documentation and code readability – Schopnost popsat kód slovy, dokumentovat postupy a zajistit, aby byl kód srozumitelný pro ostatní.

Volitelné kritéria dle charakteru a technologie:

* Machine learning / scientific quality – Volba modelu, správná příprava dat a metriky vyhodnocení.  
* Databáze – Návrhu schématu, optimalizaci dotazů a zajištění integrity dat.  
* Sítě – Schopnost zajistit a řídit komunikaci mezi uzly, bezpečnost a spolehlivost.  
* Weby – UX/UI v prostředí webových služeb, bezpečnost, výkon a responzivita.

# **Sample Test Case**

**Test Case ID:** Fun_10  
**Test Designed by:** <Name1> <Name2>  
**Test Name:** Verify login with valid username and password  
**Brief description:** Test the Google login page  
**Pre-conditions:** What is need to be done before testing  
**Dependencies and Requirements:** Software, Hardware and other requirements

| Step | Test Steps | Test Data | Expected Result | Notes |
| ----- | ----- | ----- | ----- | ----- |
| 1 |  |  |  |  |
| 2 |  |  |  |  |
| 3 |  |  |  |  |
| 4 |  |  |  |  |
| 5 |  |  |  |  |

