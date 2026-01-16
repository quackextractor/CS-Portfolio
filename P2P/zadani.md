# Projekt s P2P - Moodle

## Important notes
 Zadání je na první pohled klasické P2P. Funkčnost bereme jako samozřejmost. Vím, že ji zvládnete. Dokonce máte možnost volby obtížnosti. To podstatné je ale jinde. Tentokrát se soustředíme hlavně na kvalitu vaší práce. Na promyšlenou analýzu, srozumitelnou dokumentaci, poctivé testování a především na schopnost znovu použít kód z dřívějších úloh nebo z Vašeho portfolia. Právě na to se vás budu ptát.
Než se pustíte do samotné realizace, prosím zastavte se a přemýšlejte.

- Udělejte si poctivou analýzu a návrh architektury i komponent.
- Vyberte si části architektury/komponenty, které už máte hotové z jiných projektů, a znovu je použijte.

Čím více takových částí dokážete smysluplně zapojit, tím lépe to bude hodnoceno. A pokud zjistíte, že ze své dosavadní práce nedokážete použít vůbec nic, berme to jako upřímnou otázku. Má ten dosavadní kód skutečnou hodnotu? Není čas ho zlepšit, zpřehlednit, zobecnit? Dřív než začnete psát další.. Možná si vytvořte vlastní podpůrné knihovny, na které pak budete moci být hrdí... a hlavně je budete moci použít. Opakovaně.


## Požadavky na absolvování

Vaším úkolem je vytvořit pomocí povolených programovacích jazyků a technologií node (uzel) dle architektonického návrhového vzoru P2P (peer to peer). Každý node bude reprezentovat banku, kterou znáte ze svého života. Banku ve které lze vytvořit bankovní účet, vložit do ní peníze nebo je vybrat. V řešení byste měli prezentovat své dovednosti ze všech předchozích úloh a využít maximum kódu, který je univerzální a lze jej využívat i v tomto projektu.

Celý P2P systém se tak bude skládat z mnoha různých bank jednotlivých žáků a dohromady tvořit velký mezibankovní systém výměny informací, který budeme testovat použitím ve třídě tak, že všichni najednou spustíme své aplikace a budeme v nich pracovat najednou. Neřešíme měnu, tedy všecny částky jsou v amerických dolarech a k aplikaci se musí dát připojit také pomocí PuTTY a posílat příkazy "ručně".

Vaše bankovní aplikace (node) musí být spustitelná na školním PC a komunikovat prostřednictvím školní PC sítě bez použití IDE a pomocí TCP/IP naslouchat na libovolném portu 65525 až 65535.

Komunikace pak bude probíhat pomocí přesně určených příkazů, které budou zasílný jako text v UTF-8 kódování. Každý příkaz musí začínat dvoupísmenným kódem příkazu, například BC. Na každý příkaz musí být zaslána také odpoveď, která bude začínat stejným kódem jako příkaz, nebo kódem chyby ER. Povolené příkazy jsou tyto:

### BC - Bank code
Příkaz BC vrací kód banky. Jako kód banky musíte použít svou aktuální IP adresu. Příkaz se používá často proto, aby se zjistilo, zdali na daném PC běží bankovní aplikace. Podobně jako například ping.

**Ukázka použití:**
```text
BC 
BC 10.1.2.3

```

První příkaz jsme poslali (`BC`) a odpověď (`BC 10.1.2.3`) jsme obdrželi zpět.

Pokud dojde k chybě může komunikace proběhnout například takto:

```text
BC
ER Chyba v aplikaci, prosím zkuste to později.

```

### AC - Account create

Příkaz AC vytvoří v bance nový bankovní účet a vrátí zpět tomu, kdo ho spustil jako odpověď číslo tohoto účtu. Číslo účtu musí být v rozmezí 10000 až 99999 a můžete ho volit jak chcete, jen se nesmí samozřejmě v rámci Vaší banky opakovat, jako ve skutečné bance.

```text
AC
AC 10001/10.1.2.3

```

V případě chyby to může vypadat například takto:

```text
AC
ER Naše banka nyní neumožňuje založení nového účtu.

```

### AD - Account deposit

Příkaz AD umožňuje vložit na bankovní účet peníze. Syntaxe je složená z kódu příkazu, který následuje mezera, pak číslo účtu, lomítko a kód banky. Dále mezera a částka.

Například vložení tří tisíc korun na bankovní účet 10001/10.1.2.3 může vypadat takto:

```text
AD 10001/10.1.2.3 3000
AD

```

Pokud ale někdo pošle například příkaz špatně, nebo nastane jiná chyba, může to vypadat třeba takto:

```text
AD neco/10.1.2.3 +3000
ER číslo bankovního účtu a částka není ve správném formátu.

```

### AW - Account withdrawal

Příkaz AW umožňuje vybrat z bankovního účtu peníze. Syntaxe i chování je stejné jako v u příkazu AD, důležité je, že se nepíše znaménko. Pokud chci vybrat dva tisíce z účtu 10001/10.1.2.3 lze to takto:

```text
AW 10001/10.1.2.3 2000
Aw

```

Pokud není dost peněz, můžete ale dopadnout i takto:

```text
AW 10001/10.1.2.3 2000
ER Není dostatek finančních prostředků.

```

### AB - Account balance

Vrací aktuální zůstatek na účtu. Použití je jednoduché:

```text
AB 10001/10.1.2.3
AB 2000

```

Pokud není dost peněz, můžete ale dopadnout i takto:

```text
AW 100/10.10.100.300
ER Formát čísla účtu není správný.

```

### AR - Account remove

Smaže bankovní účet, ale pozor - pouze pokud je zůstatek 0. Jednoduše funuguje takto:

```text
AR 10001/10.1.2.3
AR

```

Ukažme si nyní na delším příkladu, jak zkontrolujeme zůstatek a pokusíme se vymazat účet. To vyhodí chybu. Následně peníze vybereme a znovu se ho pokusíme vymazat, což už proběhne bez problémů:

```text
AB 89500/10.1.2.3
AB 2000
AR 89500/10.1.2.3
ER Nelze smazat bankovní účet na kterém jsou finance.
AW 89500/10.1.2.3 2000
AW
AR 89500/10.1.2.3
AR

```

### BA - Bank (total) amount

Příkaz BA zjistí celkový součet všech finančních prostředků ve Vaší bance, tj. na všech účtech dohromady. Je to jednoduché, například takto lze zjistit, že v této bance je sedm miliónu a nějaké drobné..

```text
BA
BA 7001211

```

### BN - Bank number (of clients)

Tento příkaz vypíše počet klientů, kteří mají v bance aktuálně bankovní účet.

```text
BN
BN 5

```

---

## Přehled všech povolených příkazů

Pro jistotu si uveďme kompletní přehled všech povolených příkazů. Jsou povoleny jen tyto příkazy a žádné jiné, nebo jiné formáty.

| Název | Kód | Volání | Odpověď při úspěchu | Odpověď při chybě |
| --- | --- | --- | --- | --- |
| Bank code | BC | BC | BC `<ip>` | ER `<message>` |
| Account create | AC | AC | AC `<account>/<ip>` | ER `<message>` |
| Account deposit | AD | AD `<account>/<ip>` `<number>` | AD | ER `<message>` |
| Account withdrawal | AW | AW `<account>/<ip>` `<number>` | AW | ER `<message>` |
| Account balance | AB | AB `<account>/<ip>` | AB `<number>` | ER `<message>` |
| Account remove | AR | AR `<account>/<ip>` | AR | ER `<message>` |
| Bank (total) amount | BA | BA | BA `<number>` | ER `<message>` |
| Bank number of clients | BN | BN | BN `<number>` | ER `<message>` |

### Vysvětlení k `<ip>`, `<account>` a `<number>`

* **`<ip>`**: IP adresa ve formátu 0.0.0.0 až 255.255.255.255, která se používá jako kód banky, tj. unikátní indentifikátor každé banky v naší síti.
* **`<account>`**: Kladné celé číslo v rozsahu 10000 až 99999 (deset tisíc až devadesát devět tisíc devět set devadesát devět).
* **`<number>`**: Nezáporné celé číslo v rozsahu 0 až 9223372036854775807 (nula až dvě na šedesátou třetí, mínus jedna, tedy velikost 64bitového datového typu, zpravidla označovaného jako long).

### Vysvětlení k příkazu ER a `<message>`

Pokud Váš program selže, nebo dostane nějaký neplatný příkaz, vrací místo správné odpovědi kód ER následovaný chybovou hláškou v českém nebo anglickém jazyce, která je od kódu oddělena mezerou. Délka není omezena, ale doporučujeme jednu větu. Na jeden problém může být jen jedna chybová hláška a pokud v ní chcete zachytit více skutečností, použijte souvětí.

---

## Konfigurace

V programu implementujte nastavitelný timetout defaultně na 5 sec pro všechny odpovědi na volání příkazů a také vytvořte timeout pro obsluhu klientů. Pokud něco potrvá déle, pracujte s tím jako s chybou. Dále musíte umět nastavit port, na kterém Vaše aplikace naslouchá a pokud nenačítate IP adresu dynamicky tak i tu. Další konfiguraci necháváme na Vás.

## Logování

Vaše aplikace musí umět správně logovat svůj provoz i provoz dalších nodu, se kterými spolupracovala. Z logů zpětně musí být dohledatelné co se děje.

## Dokumentace

Dokumentace k programu musí obsahovat způsob spuštění i ovládání aplikace a také další dvě povinné položky:

1. Použité zdroje, ze kterých jste čerpali. Pokud použijete k vytvoření ChatGPT nebo jinou AI, uveďte link na konkrétní rozhovor a promptování.
2. Seznam odkazů na zdrojový kód, který je znovypoužitý z předchozích projektů.

Kvalitu použitých zdrojů a množství kódu, který se Vám podařílo znovu-použít z předchozích projektů budeme hodnotit a to tak, že v případě neexistence nebo nekvality zdrojů, či neschopnosti použít znovu svůj starší zdrojový kód zhoršíme známku jeden nebo dva stupně.

---

## Známkování

V tomto projektu si skupinu vybíráte samostatně. Pozor ale na to, že některé skupiny při splnění zadání mohou přínést například maximálně známku 3 - dobrý nebo 4 - dostatečný a jen jedna skupina zadání umožní získat známku 1 - výborný. Volte si tedy chytře a s vědomím toho, že práci musíte obhájit a je i možné, že ji bude testovat jiná osoba. Můžete být i požádání o rozšíření nebo změnu, některých konstrukcí. Lehčí zadání Vám tedy umožní snažší obhajobu, větší šanci při testování, ale lze dosáhnout jen hoších známek. Těžší zadání umožní získat třeba i jedničku, ale za cenu obhajoby i testování ve složitějším režimu, protože zadání vyžaduje složitější řešení.

### BASIC BANK NODE

Vytvořte výše uvedené zadání tak jak je, bez chyb podle kritérií hodnocení, tj. včetně testování, konfigurovatelnost a s dobrou architekturou tak, aby se při vypnutí nebo restartu aplikace neztratila informace o bankovních účtech a jejich částkách.

**Možné známky:** 3 - dobrý, 4 - dostatečný, nebo 5 - nedostatečný.

### ESSENTIALS BANK NODE

Vytvořte výše uvedené zadání podle BASIC BANK NODE a přidejte funkcionalitu tak, aby příkazy AD, AW, AB pokud přijmou jiný kód banky (ip adresu), než tu kterou má Vaše aplikace fungovali jako proxy. To znamená připojili se na aplikaci Vašeho spolužáka podle zadané ip adresy (kódu banky), příkaz provedli a vrátily výsledek.

**Možné známky:** 2 - chvalitebný, 3 - dobrý, 4 - dostatečný, nebo 5 - nedostatečný.

### HACKER BANK NODE

Vytvořte výše uvedené zadání podle ESSENTIALS BANK NODE a přidejte funkcionalitu jako příkaz RP - robbery plan se syntaxí `RP <number>` pouze pro Váš server, která umožní vypsat plán loupeže podle aktuálního stavu P2P sítě s tím, že lze vyloupit vždy a pouze celou banku nebo nic.

Uživatel zadá cílovou částku pro loupež. Například `RP 1000000`.
Aplikace projde celou síť a zjistí kolik peněz je aktuálně v které bance a kolik klientů tam je.

Například:

* 10.1.2.3 má celkem 500000 a 10 klientů
* 10.1.2.4 má celkem 100200 a 2 klienty
* atd. atd..

Loupež se naplánuje tak, aby se dosáhlo co nejblíže cílové částce a zároveň bylo okradeno co nejméně klientů. Odpovědí na příkaz bude seznam bank k vyloupení ve formátu `RP <message>`. Text je na Vás, například:

```text
RP K dosažení 1000000 je třeba vyloupit banky 10.1.2.3 a 10.1.2.85 a bude poškozeno jen 21 klientů.

```

**Možné známky:** jakékoliv.

---

## FAQ a časté chyby

* Nesnažte se programovat klienta, použijte PuTTy nebo telnet.
* Nepleťe si to P2P s architekturou klient/server, tu zde neprogramujeme.
* Neměňte příkazy, používejte výhradně ty povolené a přesně v tom tvaru, v jaké mají být. Když si zavedete vlastní příkazy, tak Váš program nepůjde projit s programy spolužáků.
* Nezapomeňte na timeouty. Je to klíčová část programu. Je třeba hlídat timeout jak při scanování sítě, tak i při každé komunikaci. Kdykoli se může každý připojený program nebo PuTTy náhle odpojit nebo dlouho nereagovat.
* Netestujte program sami, vždy testujte propojení Vašeho programu s programy spolužáků. Nakonec bude třeba postavit síť těchto propojení, takže je celkem jedno, zda-li Vám program pracuje na localhostu... důležité je, aby spolupracoval s programy dalších lidí.
* Nezapomeňte, že program nemusí mít žádné UI, ale musí logovat.
* Program by měl pracovat s více klienty paralerně a měl by využívat fyzickou paralerizaci, proto si dejte pozor knihovny, které poskytují jen souběžnost, ale skutečně paralerně neběží..
* Program který jen funguje nestačí! Nezapomeňte, že hodnotíme především Vás. Vymyslete vlastní rozšíření, vylepšení, architekturu, monitoring, sledování a statisticky sítě apod.
* Zprávy jsou jednořádkové. Víceřadkové zprávy neodpovídají komunikačnímu protokolu. Tedy každá zpráva končí znakem pro zalomení řádku.
* Způsob trvalého uložení dat je volbou autora. Budeme ale hodnotit jak kvalitní volbu autor udělal. Nic nezakazujeme, ale samozřejmě doporučujeme vždy volbě přizpůsobit architekturu aplikace tak, aby žák předvedl co nejvíce svých znalostí. Na achitektuře ve vztahu k persistentnímu úložišti a případně na návrhových vzorech nejen v této oblasti záleží více, než na tom který typ úložiště byl zvolen, pokud nebyl zvolen úplně nevhodně.
* Hodnocení znovu-použítí kódu je založeno na tom, že žák dokáže využít svůj předchozí zdrojový kód tak, že ušetří co nejvyšší množství MD, MH (man-day, man-hour) a nebo jeho použítí bylo jinak užitečné. Vyšší míra užitečného využití vlastního kódu z autorovy předchozí práce bude hodnocena velmi kladně a naopak neschopnost použít nic, ze své předchozí práce značí velký problém.
* Program po přijetí příkazu odpoví, ale neměl by automaticky odpojit klienta. Spojení by měl ukončovat klient, který ho začal. Není tedy správné v případě, že přijde nějaký příkaz ho sice splnit ale následně spojení ukončit dříve, než byde timeout.
* Velikost písmen (malá, velká), jinak nazývaná case-senstive zde není určena. Příkazy v ukázkách jsou velkými písmeny a ty musí fungovat vždy. Pokud program vytvoříte tak, že bude akceptovat i malá písmena, může to být výhoda. Nelze ale garantovat, že ostatní programy Vašich spolužáků budou malá písmena akceptovat.

(pokud máte nějakou otázku k zadání, pošlete na mandik@spsejecna.cz a my zde zveřejníme odpověď)

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

