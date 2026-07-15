# 9. Realna primera: steklo in DPOSS

Realni primeri v izvirnem članku niso samo ilustracije. Pokažejo, da je diagnostična vrednost MacroPCA vezana na spremenljivke, ne samo na opazovanja.

## Stekleni vzorci

Pri podatkih o steklu so vrstice vzorci, stolpci pa kemijske koncentracije. Klasična ali zgolj vrstično robustna analiza lahko označi nenavadne vzorce, vendar je za interpretacijo pomembno vedeti, katere kemijske spremenljivke povzročajo odstopanje.

Residualna karta je tu naravno orodje. Če vzorec odstopa zaradi določenega elementa ali kombinacije elementov, metoda pokaže lokaliziran vzorec residualov. Domenski strokovnjak lahko nato presodi, ali gre za merilno napako, drugačen izvor materiala ali legitimno redko sestavo.

## DPOSS zvezde

DPOSS primer je drugačen, ker vključuje veliko manjkajočih vrednosti. To je dober stresni test za metodo: algoritem mora hkrati delati z nepopolnostjo in z anomalijami. Pri astronomskih podatkih manjkajočnost ni zgolj tehnična nadloga; pogosto je povezana z opazovalnimi omejitvami in lastnostmi merjenja.

MacroPCA v takem okolju omogoči, da se struktura podatkov ne sesuje v množici manjkajočih celic. Hkrati residualna diagnostika pokaže, katere zvezde in katere spremenljivke zaslužijo nadaljnjo pozornost.

## Zakaj ne zadostuje seznam osamelcev

Če metoda vrne samo seznam sumljivih vrstic, je uporabna za filtriranje, ne pa nujno za razumevanje. MacroPCA je močnejša, ker lahko pove:

- ali je vrstica odmaknjena znotraj podprostora,
- ali je slabo rekonstruirana s podprostorom,
- katere celice imajo velike residuale,
- ali je problem lokaliziran ali celostno vrstičen.

To je razlika med detekcijo in diagnostiko. Detekcija odgovori na vprašanje »kaj je sumljivo«. Diagnostika odgovori tudi na vprašanje »zakaj je sumljivo«.

## Uporaba izvirnih figur

Izvirni članek vsebuje informativne residualne karte, karte osamelcev in simulacijske grafe. Ker licenca vključuje omejitev NoDerivatives, ta knjiga ne predeluje teh figur. Če jih učitelj uporabi pri seminarju, naj jih uporabi nespremenjene, z navedbo avtorjev, članka, revije in DOI.
