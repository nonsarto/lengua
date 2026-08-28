# GRAMMAR_REVIEW — Temario-Lektionen zum Gegenlesen

Von Opus generiert, von dir eingefroren. Korrigiere direkt in
`db/seed/grammar_lessons.json` (diese Datei ist nur die Leseansicht). Erfahrungsgemäß
prüfen: erfundene unregelmäßige Formen, fehlende vosotros-Spalte, generische
note-Blöcke, und das concept_slug-Mapping in grammar_catalog.py. Wenn alles stimmt:
`python grammar_catalog.py push` und danach `python grammar_catalog.py approve`.

**39/39 Lektionen**

## `articulos-definidos` — Artículos Definidos  (A1)
*el, la, los, las — der bestimmte Artikel* · Konzept: `articulos`

Der bestimmte Artikel (artículos definidos) steht vor Substantiven, die schon bekannt oder eindeutig sind. Er entspricht dem deutschen der, die, das. Im Spanischen richtet er sich in Geschlecht und Zahl nach dem Substantiv und wird deshalb in vier Formen verwendet.

### Die vier Formen

**Bestimmte Artikel nach Geschlecht und Zahl**
|  | Singular | Plural |
|---|---|---|
| maskulin | el | los |
| feminin | la | las |

**Beispiele mit Substantiv**
|  | Beispiel |
|---|---|
| el (m. Sg.) | el libro |
| la (f. Sg.) | la casa |
| los (m. Pl.) | los libros |
| las (f. Pl.) | las casas |

### Verwendung

- **Etwas Bekanntes oder bereits Erwähntes** — _El coche está en la calle._ (Das Auto steht auf der Straße.)
- **Eindeutiges, Einmaliges** — _El sol brilla hoy._ (Die Sonne scheint heute.)
- **Allgemeine Aussagen über eine ganze Gruppe** — _Los gatos duermen mucho._ (Katzen schlafen viel.)
- **Bei Wochentagen (regelmäßige Ereignisse)** — _Trabajo los lunes._ (Ich arbeite montags.)
- **Bei Körperteilen statt Possessiv** — _Me duele la cabeza._ (Mir tut der Kopf weh.)

### Besonderheiten

**Verschmelzung mit a und de**
|  | Verschmelzung | Beispiel |
|---|---|---|
| a + el | al | Voy al mercado. |
| de + el | del | La puerta del coche. |

> ⚠️ Deutsche Muttersprachler übertragen oft das deutsche Genus. Aber das Geschlecht kann abweichen: Es heißt 'la leche' (die Milch, feminin – wie im Deutschen), aber 'el problema' (das Problem, maskulin trotz Endung -a) und 'la mano' (die Hand, feminin trotz Endung -o). Der Artikel muss immer mit dem spanischen Genus gelernt werden, nicht aus dem Deutschen abgeleitet.

## `articulos-indeterminados` — Artículos Indeterminados  (A1)
*un, una, unos, unas — der unbestimmte Artikel* · Konzept: `articulos`

Der unbestimmte Artikel (artículo indeterminado) steht vor Substantiven, die nicht näher bestimmt sind oder zum ersten Mal erwähnt werden. Auf Deutsch entspricht er »ein, eine«. Im Plural (unos, unas) bedeutet er »einige« oder »ein paar«.

### Die Formen

**Unbestimmte Artikel nach Genus und Numerus**
|  | Singular | Plural |
|---|---|---|
| maskulin | un | unos |
| feminin | una | unas |

### Beispiele mit Substantiv

**Der Artikel richtet sich nach Genus und Numerus des Substantivs**
|  | maskulin | feminin |
|---|---|---|
| Singular | un libro | una casa |
| Plural | unos libros | unas casas |

### Verwendung

- **Etwas zum ersten Mal erwähnen** — _Hay un perro en el jardín._ (Es ist ein Hund im Garten.)
- **Eine unbestimmte Menge (Plural)** — _He comprado unas manzanas._ (Ich habe ein paar Äpfel gekauft.)
- **Eine ungefähre Zahl angeben** — _Vinieron unas veinte personas._ (Es kamen ungefähr zwanzig Personen.)
- **Eine Eigenschaft betonen** — _Es una casa muy grande._ (Es ist ein sehr großes Haus.)

### Besonderheit: un vor femininen Substantiven

**Feminine Substantive, die mit betontem a- oder ha- beginnen, nehmen im Singular un**
|  | Singular | Plural |
|---|---|---|
| agua (f.) | un agua | unas aguas |
| águila (f.) | un águila | unas águilas |

> ⚠️ Deutschsprachige lassen den unbestimmten Artikel oft weg oder setzen ihn falsch bei Berufen: Nach »ser« steht der Beruf ohne Artikel — »Soy médico« (nicht »Soy un médico«). Der Artikel erscheint erst, wenn ein Adjektiv folgt: »Soy un médico excelente«.

## `genero-numero-sustantivo` — Género y Número del Sustantivo  (A1)
*Genus und Plural der Substantive* · Konzept: `genero-y-numero`

Jedes spanische Substantiv hat ein Genus (männlich oder weiblich) und einen Numerus (Singular oder Plural). Genus und Numerus bestimmen, welchen Artikel und welche Adjektivendung du verwendest. Deshalb lohnt es sich, beides von Anfang an mitzulernen.

### Genus: typische Endungen

**Häufige Endungen für männliche und weibliche Substantive**
| Endung | Genus | Beispiel |
|---|---|---|
| -o | meist männlich | el libro (das Buch) |
| -a | meist weiblich | la mesa (der Tisch) |
| -or | meist männlich | el color (die Farbe) |
| -ción, -sión | weiblich | la canción (das Lied) |
| -dad, -tad | weiblich | la ciudad (die Stadt) |

### Pluralbildung

**Regeln für den Plural**
| Wortende | Regel | Singular → Plural |
|---|---|---|
| Vokal | + -s | el gato → los gatos |
| Konsonant | + -es | el papel → los papeles |
| -z | -z wird zu -c + -es | el lápiz → los lápices |

### Verwendung

- **Passenden Artikel wählen** — _El coche es nuevo y la casa es grande._ (Das Auto ist neu und das Haus ist groß.)
- **Vom Singular zum Plural** — _Tengo un amigo. Tengo tres amigos._ (Ich habe einen Freund. Ich habe drei Freunde.)
- **Weibliche Endungen erkennen** — _La libertad y la información son importantes._ (Die Freiheit und die Information sind wichtig.)
- **Plural bei gemischten Gruppen** — _Los padres están en casa._ (Die Eltern sind zu Hause.)

### Ausnahmen und Sonderfälle

**Wörter, die der Endungsregel widersprechen**
| Wort | Genus | Bedeutung |
|---|---|---|
| el día | männlich | der Tag (endet auf -a) |
| la mano | weiblich | die Hand (endet auf -o) |
| el problema | männlich | das Problem (endet auf -a) |
| el mapa | männlich | die Landkarte (endet auf -a) |
| la foto | weiblich | das Foto (Kurzform von la fotografía) |

> ⚠️ Verlass dich nicht auf das deutsche Genus: Spanisch und Deutsch stimmen oft nicht überein. 'die Milch' ist im Spanischen männlich? Nein – aber 'der Tisch' ist weiblich (la mesa) und 'das Auto' ist männlich (el coche). Lern jedes Substantiv immer zusammen mit seinem Artikel.

## `adjetivos-concordancia-posicion` — Adjetivos: Concordancia y Posición  (A1)
*Angleichung und Stellung der Adjektive* · Konzept: `concordancia-adjetivo`

Adjektive beschreiben Substantive, zum Beispiel ihre Farbe, Größe oder Eigenschaft. Im Spanischen richten sie sich in Geschlecht und Zahl nach dem Substantiv und stehen meistens dahinter. Das ist grundlegend, um im Alltag Dinge und Personen korrekt zu beschreiben.

### Angleichung in Geschlecht und Zahl

**Adjektive auf -o (vier Formen)**
|  | männlich | weiblich |
|---|---|---|
| Singular | el coche rojo | la casa roja |
| Plural | los coches rojos | las casas rojas |

**Adjektive auf -e oder Konsonant (zwei Formen)**
|  | Singular | Plural |
|---|---|---|
| auf -e (grande) | un libro grande / una mesa grande | libros grandes / mesas grandes |
| auf Konsonant (azul) | un jersey azul / una falda azul | jerséis azules / faldas azules |

### Verwendung

- **Eigenschaft einer Person beschreiben** — _Mi hermana es muy alta._ (Meine Schwester ist sehr groß.)
- **Angleichung im Plural** — _Los pisos nuevos son caros._ (Die neuen Wohnungen sind teuer.)
- **Adjektiv nach dem Substantiv** — _Quiero una camisa blanca._ (Ich möchte ein weißes Hemd.)
- **Ein Adjektiv für zwei Substantive (männlich Plural)** — _El padre y la madre están cansados._ (Der Vater und die Mutter sind müde.)

### Stellung: einige Adjektive stehen davor

**Vorangestellte Adjektive und Kurzformen**
|  | vor Substantiv | Beispiel |
|---|---|---|
| bueno | buen (vor männl. Sing.) | un buen amigo |
| malo | mal (vor männl. Sing.) | un mal día |
| grande | gran (Sing. m/w) | una gran ciudad |
| Ordnungszahl | primer, tercer (vor männl. Sing.) | el primer piso |

> ⚠️ Deutsche stellen das Adjektiv oft vor das Substantiv, wie im Deutschen ('ein rotes Auto'). Im Spanischen steht es normalerweise dahinter: 'un coche rojo', nicht 'un rojo coche'.

## `pronombres-personales` — Pronombres Personales  (A1)
*Die Subjektpronomen: yo, tú, él …* · Konzept: `—`

Die pronombres personales sind die Subjektpronomen: sie ersetzen die handelnde Person im Satz. Im Spanischen werden sie oft weggelassen, weil die Verbendung schon zeigt, wer gemeint ist. Wichtig sind sie aber zur Betonung, zum Kontrast und in der höflichen Anrede.

### Die Formen

**Subjektpronomen im Überblick**
|  | Singular | Plural |
|---|---|---|
| 1. Person | yo | nosotros, nosotras |
| 2. Person | tú | vosotros, vosotras |
| 3. Person | él, ella, usted | ellos, ellas, ustedes |

nosotras, vosotras und ellas werden nur verwendet, wenn die Gruppe ausschließlich aus weiblichen Personen besteht. Sobald mindestens ein Mann dabei ist, stehen die maskulinen Formen nosotros, vosotros, ellos. usted und ustedes sind die höflichen Anredeformen, werden aber grammatisch mit der 3. Person verbunden.

### Verwendung

- **Betonung oder Kontrast** — _Yo trabajo en Madrid, pero ella vive en Sevilla._ (Ich arbeite in Madrid, aber sie wohnt in Sevilla.)
- **Höfliche Anrede (Sie)** — _¿Usted quiere un café?_ (Möchten Sie einen Kaffee?)
- **Vertraute Anrede in Spanien (ihr)** — _¿Vosotros venís a la fiesta?_ (Kommt ihr zur Party?)
- **Weggelassen, weil klar aus dem Verb** — _Hablo español._ (Ich spreche Spanisch.)

### Besonderheiten in Spanien

**Anrede: vertraut vs. höflich**
|  | vertraut | höflich |
|---|---|---|
| Singular | tú | usted |
| Plural | vosotros, vosotras | ustedes |

> ⚠️ Deutschsprachige benutzen die Subjektpronomen zu oft. Da die Verbendung die Person schon anzeigt, klingt 'Yo soy alemán, yo vivo en España, yo trabajo aquí' unnatürlich. Setze das Pronomen nur bei Betonung oder Kontrast; normalerweise reicht 'Soy alemán, vivo en España, trabajo aquí'.

## `pronombres-posesivos` — Pronombres Posesivos  (A1)
*mi, tu, su — Possessivbegleiter und -pronomen* · Konzept: `posesivos`

Possessivbegleiter (posesivos) drücken aus, wem etwas gehört: mein Haus, dein Auto, seine Katze. Sie stehen vor dem Substantiv und richten sich in der Anzahl (Singular/Plural) danach, bei nuestro und vuestro auch im Geschlecht. Sie ersetzen dabei den Artikel.

### Die Possessivbegleiter (unbetonte Form)

**Formen im Singular und Plural des besessenen Objekts**
|  | ein Objekt (Singular) | mehrere Objekte (Plural) |
|---|---|---|
| yo | mi | mis |
| tú | tu | tus |
| él, ella, usted | su | sus |
| nosotros, nosotras | nuestro / nuestra | nuestros / nuestras |
| vosotros, vosotras | vuestro / vuestra | vuestros / vuestras |
| ellos, ellas, ustedes | su | sus |

Wichtig: mi, tu, su und ihre Pluralformen haben nur eine Geschlechtsform. Nur nuestro und vuestro unterscheiden zwischen männlich (-o) und weiblich (-a).

### Verwendung

- **Besitz einer Person** — _Mi coche está en la calle._ (Mein Auto steht auf der Straße.)
- **Zugehörigkeit im Plural (Objekt)** — _Tus llaves están en la mesa._ (Deine Schlüssel liegen auf dem Tisch.)
- **Übereinstimmung mit nosotros** — _Nuestra casa es muy grande._ (Unser Haus ist sehr groß.)
- **Vosotros-Form (Spanien)** — _¿Dónde están vuestros hijos?_ (Wo sind eure Kinder?)
- **Familie und Beziehungen** — _Su madre vive en Sevilla._ (Seine/ihre Mutter wohnt in Sevilla.)

### Die betonte Form (Possessivpronomen)

**Betonte Formen, oft mit Artikel: el mío, la tuya …**
|  | männlich Sg. | weiblich Sg. | männlich Pl. | weiblich Pl. |
|---|---|---|---|---|
| yo | mío | mía | míos | mías |
| tú | tuyo | tuya | tuyos | tuyas |
| él, ella, usted | suyo | suya | suyos | suyas |
| nosotros, nosotras | nuestro | nuestra | nuestros | nuestras |
| vosotros, vosotras | vuestro | vuestra | vuestros | vuestras |
| ellos, ellas, ustedes | suyo | suya | suyos | suyas |

Die betonte Form steht nach dem Substantiv (un amigo mío = ein Freund von mir) oder allein mit Artikel (el mío = meiner). Beispiel: Esta maleta es mía. (Dieser Koffer gehört mir.)

> ⚠️ Der häufigste Fehler: die Possessivbegleiter mit dem Geschlecht des Besitzers statt des Objekts abgleichen. Es heißt su casa – egal ob 'er', 'sie' oder 'Sie' gemeint ist. Und mi, tu, su bekommen NIE ein -a oder -o (nicht 'mia casa', sondern mi casa).

## `ser-estar-tener` — Verbos Ser, Estar y Tener  (A1)
*Die Grundverben: sein und haben* · Konzept: `ser-vs-estar`

Ser, estar und tener sind die drei wichtigsten Grundverben. Ser drückt dauerhafte Eigenschaften und Identität aus, estar bezeichnet Zustände und Orte, und tener bedeutet haben oder besitzen. Ohne diese drei Verben lässt sich kaum ein Satz bilden, deshalb bilden sie das Fundament des Spanischen.

### Die Konjugation im Präsens

**Ser, estar und tener im Presente de indicativo**
|  | ser | estar | tener |
|---|---|---|---|
| yo | soy | estoy | tengo |
| tú | eres | estás | tienes |
| él, ella, usted | es | está | tiene |
| nosotros, nosotras | somos | estamos | tenemos |
| vosotros, vosotras | sois | estáis | tenéis |
| ellos, ellas, ustedes | son | están | tienen |

### Verwendung

- **Ser: Identität, Beruf, Herkunft** — _Soy alemana y soy profesora._ (Ich bin Deutsche und ich bin Lehrerin.)
- **Ser: dauerhafte Eigenschaften** — _La casa es grande y blanca._ (Das Haus ist groß und weiß.)
- **Estar: Ort** — _El supermercado está en la esquina._ (Der Supermarkt ist an der Ecke.)
- **Estar: vorübergehender Zustand** — _Hoy estoy muy cansado._ (Heute bin ich sehr müde.)
- **Tener: Besitz und Alter** — _Tengo dos hijos y tengo cuarenta años._ (Ich habe zwei Kinder und ich bin vierzig Jahre alt.)

### Feste Ausdrücke mit tener

**Häufige Wendungen, in denen tener statt ser oder estar steht**
| Spanisch | Deutsch |
|---|---|
| tener hambre | Hunger haben |
| tener sed | Durst haben |
| tener frío | frieren / kalt haben |
| tener calor | warm haben / schwitzen |
| tener miedo | Angst haben |
| tener razón | recht haben |
| tener ... años | ... Jahre alt sein |

> ⚠️ Verwechsle ser und estar nicht: Deutsch hat nur „sein". Ort und vorübergehender Zustand verlangen estar (Estoy en Madrid, estoy enfermo), Identität und dauerhafte Eigenschaft verlangen ser (Soy médico). Und Alter oder Hunger stehen mit tener: sag Tengo treinta años, niemals „soy treinta años", und Tengo hambre, nicht „estoy hambre".

## `hay-estar` — Hay / Estar  (A1)
*„es gibt“ vs. „sich befinden“* · Konzept: `estar-vs-hay`

Mit hay und estar drückst du im Spanischen unterschiedliche Dinge aus: hay bedeutet „es gibt“ und benennt die bloße Existenz von etwas. Estar bedeutet „sich befinden“ und beschreibt, wo etwas Bestimmtes liegt. Die Unterscheidung ist wichtig, weil beide im Deutschen oft mit „ist“ übersetzt werden.

### Die beiden Formen im Überblick

**Hay ist unveränderlich; estar wird konjugiert.**
|  | Form |
|---|---|
| hay (Existenz) | hay |
| yo | estoy |
| tú | estás |
| él, ella, usted | está |
| nosotros, nosotras | estamos |
| vosotros, vosotras | estáis |
| ellos, ellas, ustedes | están |

Faustregel: hay steht mit unbestimmten Dingen (un, una, unos, unas), mit Zahlen oder mit unbestimmten Mengen. Estar steht mit bestimmten Dingen (el, la, los, las), mit Eigennamen oder mit Possessivbegleitern.

### Verwendung

- **Existenz benennen (hay)** — _En la plaza hay un supermercado._ (Auf dem Platz gibt es einen Supermarkt.)
- **Menge oder Zahl angeben (hay)** — _Hay tres bancos en esta calle._ (Es gibt drei Banken in dieser Straße.)
- **Standort von etwas Bestimmtem (estar)** — _El supermercado está al lado de la farmacia._ (Der Supermarkt befindet sich neben der Apotheke.)
- **Wo sich Personen befinden (estar)** — _Mis padres están en casa._ (Meine Eltern sind zu Hause.)
- **Nach dem Weg fragen (estar)** — _¿Dónde está el baño, por favor?_ (Wo ist die Toilette, bitte?)

### Bestimmt oder unbestimmt: der Unterschied im Satz

**Derselbe Ort, aber andere Perspektive.**
|  | hay (unbestimmt) | estar (bestimmt) |
|---|---|---|
| Beispiel | Hay una parada de metro cerca. | La parada de metro está cerca. |
| Deutsch | Es gibt eine Metrostation in der Nähe. | Die Metrostation ist in der Nähe. |

> ⚠️ Deutsche Muttersprachler sagen oft fälschlich „El supermercado hay al lado de la farmacia“. Mit einem bestimmten Artikel (el, la, los, las), Eigennamen oder Possessiv muss estar stehen: „El supermercado está al lado de la farmacia.“ Hay verwendest du nie zusammen mit el, la, los oder las.

## `muy-mucho` — Muy / Mucho  (A1)
*sehr vs. viel* · Konzept: `muy-vs-mucho`

Muy und mucho werden im Deutschen oft beide mit „sehr" oder „viel" wiedergegeben, funktionieren aber unterschiedlich. Muy verstärkt Adjektive und Adverbien, mucho drückt eine große Menge oder Intensität aus. Wer beide unterscheidet, vermeidet einen der häufigsten A1-Fehler.

### Die Grundregel

**Muy und mucho im Überblick**
| Wort | Funktion | Veränderlich? |
|---|---|---|
| muy | verstärkt Adjektiv oder Adverb | unveränderlich |
| mucho/-a/-os/-as | Menge vor Substantiv | richtet sich nach Genus und Numerus |
| mucho | Intensität nach Verb | unveränderlich |

### Formen von mucho vor dem Substantiv

**Anpassung von mucho an das Substantiv**
|  | männlich | weiblich |
|---|---|---|
| Singular | mucho | mucha |
| Plural | muchos | muchas |

### Verwendung

- **Muy vor einem Adjektiv** — _La casa es muy grande._ (Das Haus ist sehr groß.)
- **Muy vor einem Adverb** — _Hablas muy bien español._ (Du sprichst sehr gut Spanisch.)
- **Mucho vor einem Substantiv (angepasst)** — _Tengo mucha hambre y muchos amigos._ (Ich habe großen Hunger und viele Freunde.)
- **Mucho nach einem Verb (unveränderlich)** — _Vosotros trabajáis mucho._ (Ihr arbeitet viel.)
- **Mucho allein für Menge** — _¿Comes mucho? — Sí, como mucho._ (Isst du viel? — Ja, ich esse viel.)

> ⚠️ Deutsche sagen oft fälschlich „muy mucho" oder „muy calor". Vor Substantiven wie calor, hambre, frío steht mucho/mucha (mucho calor, mucha hambre), niemals muy. Und muy kombiniert nie direkt mit mucho: für „sehr viel" sagt man muchísimo, nicht „muy mucho".

## `presente-indicativo-1` — Presente de Indicativo I  (A1)
*Regelmäßige Verben im Präsens* · Konzept: `presente-indicativo`

Das Presente de Indicativo beschreibt Handlungen in der Gegenwart, regelmäßige Abläufe und allgemeine Tatsachen. Spanische Verben enden im Infinitiv auf -ar, -er oder -ir. Bei regelmäßigen Verben wird die Endung abgetrennt und durch die passende Personalendung ersetzt.

### Die drei Konjugationen

**Beispielverben: hablar (sprechen), comer (essen), vivir (leben)**
|  | hablar (-ar) | comer (-er) | vivir (-ir) |
|---|---|---|---|
| yo | hablo | como | vivo |
| tú | hablas | comes | vives |
| él, ella, usted | habla | come | vive |
| nosotros, nosotras | hablamos | comemos | vivimos |
| vosotros, vosotras | habláis | coméis | vivís |
| ellos, ellas, ustedes | hablan | comen | viven |

### Die Endungen im Überblick

**Personalendungen der regelmäßigen Verben**
|  | -ar | -er | -ir |
|---|---|---|---|
| yo | -o | -o | -o |
| tú | -as | -es | -es |
| él, ella, usted | -a | -e | -e |
| nosotros, nosotras | -amos | -emos | -imos |
| vosotros, vosotras | -áis | -éis | -ís |
| ellos, ellas, ustedes | -an | -en | -en |

### Verwendung

- **Gewohnheiten und Routinen** — _Todos los días trabajo en casa._ (Jeden Tag arbeite ich zu Hause.)
- **Allgemeine Tatsachen** — _Los españoles cenan muy tarde._ (Die Spanier essen sehr spät zu Abend.)
- **Aktuelle Handlungen** — _Ahora leo el periódico._ (Jetzt lese ich die Zeitung.)
- **Vorlieben und Meinungen ausdrücken** — _Comemos mucha fruta en verano._ (Im Sommer essen wir viel Obst.)

> ⚠️ Weil das Subjekt aus der Verbendung hervorgeht, werden die Personalpronomen (yo, tú ...) meist weggelassen. Deutschsprachige setzen sie oft aus Gewohnheit dazu: nicht 'yo hablo español' im Normalfall, sondern einfach 'hablo español'. Das Pronomen wird nur zur Betonung oder zum Kontrast verwendet.

## `pronombres-demostrativos` — Pronombres Demostrativos  (A1)
*este, ese, aquel — Zeigewörter* · Konzept: `demostrativos`

Die pronombres demostrativos (Demonstrativa) zeigen auf Dinge oder Personen und drücken deren Nähe zum Sprecher aus. Sie unterscheiden drei Entfernungen: este (hier bei mir), ese (dort bei dir) und aquel (weiter weg). Sie richten sich in Genus und Numerus nach dem Substantiv.

### Die Formen der Demonstrativa

**este – Nähe zum Sprecher (hier)**
|  | männlich | weiblich |
|---|---|---|
| Singular | este | esta |
| Plural | estos | estas |

**ese – Nähe zum Angesprochenen (da)**
|  | männlich | weiblich |
|---|---|---|
| Singular | ese | esa |
| Plural | esos | esas |

**aquel – entfernt von beiden (dort drüben)**
|  | männlich | weiblich |
|---|---|---|
| Singular | aquel | aquella |
| Plural | aquellos | aquellas |

### Verwendung

- **Etwas Nahes zeigen** — _Este libro es muy interesante._ (Dieses Buch (hier) ist sehr interessant.)
- **Etwas beim Gesprächspartner zeigen** — _¿Me pasas esa botella?_ (Reichst du mir diese Flasche (da)?)
- **Etwas Entferntes zeigen** — _Aquella montaña es la más alta._ (Jener Berg (dort drüben) ist der höchste.)
- **Zeitliche Nähe ausdrücken** — _Esta semana tengo mucho trabajo._ (Diese Woche habe ich viel Arbeit.)
- **Allein stehend als Pronomen** — _No quiero este, prefiero ese._ (Ich will nicht diesen, ich bevorzuge jenen.)

### Neutrale Formen: esto, eso, aquello

**Für nicht identifizierte Dinge oder ganze Sachverhalte (unveränderlich)**
| Form | Bedeutung | Beispiel |
|---|---|---|
| esto | das hier | ¿Qué es esto? |
| eso | das da | Eso no es verdad. |
| aquello | das dort | Aquello fue increíble. |

> ⚠️ Die neutralen Formen esto, eso, aquello nie mit einem Substantiv kombinieren. Falsch ist 'esto libro' – vor einem maskulinen Substantiv steht este libro. Esto/eso/aquello stehen nur allein, wenn die Sache unbekannt oder abstrakt ist (¿Qué es esto?).

## `interrogativos` — Interrogativos  (A1)
*Fragewörter: qué, cuál, quién …* · Konzept: `interrogativos`

Interrogativos sind Fragewörter, mit denen man gezielt nach Personen, Dingen, Orten, Zeit oder Gründen fragt. Sie stehen am Anfang der Frage und tragen im Spanischen immer einen Akzent (Tilde). Ohne sie kann man nur Ja/Nein-Fragen stellen.

### Die wichtigsten Fragewörter

**Fragewörter und ihre Bedeutung**
| Fragewort | Bedeutung |
|---|---|
| ¿qué? | was? / welche(r)? |
| ¿cuál? / ¿cuáles? | welche(r)? (Auswahl) |
| ¿quién? / ¿quiénes? | wer? |
| ¿cómo? | wie? |
| ¿dónde? | wo? |
| ¿adónde? | wohin? |
| ¿cuándo? | wann? |
| ¿cuánto? / ¿cuánta? / ¿cuántos? / ¿cuántas? | wie viel? / wie viele? |
| ¿por qué? | warum? |

### Formen mit Angleichung

**quién, cuál und cuánto passen sich an**
|  | Singular | Plural |
|---|---|---|
| quién (Person) | quién | quiénes |
| cuál (Auswahl) | cuál | cuáles |
| cuánto (maskulin) | cuánto | cuántos |
| cuánta (feminin) | cuánta | cuántas |

### Verwendung

- **Nach einer Sache oder Definition fragen** — _¿Qué es esto?_ (Was ist das?)
- **Aus einer Auswahl wählen (cuál)** — _¿Cuál prefieres, el rojo o el azul?_ (Welchen bevorzugst du, den roten oder den blauen?)
- **Nach einer Person fragen** — _¿Quiénes son vuestros amigos?_ (Wer sind eure Freunde?)
- **Nach Ort und Zeit fragen** — _¿Dónde vivís y cuándo llegáis?_ (Wo wohnt ihr und wann kommt ihr an?)
- **Nach Menge fragen (angeglichen)** — _¿Cuántas hermanas tienes?_ (Wie viele Schwestern hast du?)

### qué oder cuál vor einem Substantiv

**Unterschied qué / cuál**
| Fragewort | Gebrauch | Beispiel |
|---|---|---|
| qué + Substantiv | fragt allgemein nach Art/Sorte | ¿Qué libro lees? |
| cuál (ohne Substantiv) | fragt nach Auswahl aus bekannten Optionen | ¿Cuál lees? |

> ⚠️ Deutsche übersetzen „welcher?“ oft mit cuál vor einem Substantiv – aber vor einem Substantiv steht im Spanien-Spanisch normalerweise qué: nicht „¿cuál libro?“, sondern „¿qué libro?“. Cuál benutzt man ohne folgendes Substantiv: „¿cuál de los libros?“.

## `conjunciones` — Conjunciones  (A2)
*Bindewörter: y, pero, porque …* · Konzept: `—`

Conjunciones sind Bindewörter. Sie verbinden Wörter, Satzteile oder ganze Sätze miteinander und drücken Beziehungen aus: Hinzufügung, Gegensatz, Grund oder Wahl. Ohne sie wirken Sätze abgehackt. Hier lernst du die wichtigsten Bindewörter des Alltags und wann man sie benutzt.

### Die wichtigsten Bindewörter

**Grundlegende Konjunktionen**
| Bindewort | Bedeutung | Funktion |
|---|---|---|
| y | und | Hinzufügung |
| o | oder | Auswahl |
| pero | aber | Gegensatz |
| porque | weil | Grund |
| también | auch | Hinzufügung |
| ni ... ni | weder ... noch | Verneinung |

### Formwechsel bei y und o

**y wird zu e, o wird zu u**
| Normalform | Sonderform | Regel |
|---|---|---|
| y | e | vor Wörtern, die mit i- oder hi- beginnen |
| o | u | vor Wörtern, die mit o- oder ho- beginnen |

### Verwendung

- **Zwei Dinge verbinden (y)** — _Compro pan y leche._ (Ich kaufe Brot und Milch.)
- **Einen Gegensatz ausdrücken (pero)** — _Quiero salir, pero está lloviendo._ (Ich will rausgehen, aber es regnet.)
- **Einen Grund angeben (porque)** — _No voy porque estoy cansado._ (Ich gehe nicht, weil ich müde bin.)
- **Eine Auswahl anbieten (o)** — _¿Tomas té o café?_ (Trinkst du Tee oder Kaffee?)
- **y wird zu e vor i-/hi-** — _Estudio español e inglés._ (Ich lerne Spanisch und Englisch.)

### porque, por qué, porqué und el porqué

**Leicht zu verwechseln**
| Form | Bedeutung | Beispiel |
|---|---|---|
| porque | weil (Antwort/Grund) | No como porque no tengo hambre. |
| por qué | warum (Frage) | ¿Por qué no vienes? |
| el porqué | der Grund (Substantiv) | No entiendo el porqué. |

> ⚠️ Verwechsle nicht das fragende '¿por qué?' (getrennt, mit Akzent = warum) mit dem antwortenden 'porque' (zusammen, ohne Akzent = weil). Deutsche schreiben oft fälschlich 'porqué' als Antwort. Richtig: '¿Por qué estudias español? — Porque vivo en España.'

## `acentuacion` — Acentuación  (A2)
*Betonung und der geschriebene Akzent* · Konzept: `—`

Die Acentuación regelt, welche Silbe im Spanischen betont wird und wann ein geschriebener Akzent (tilde) nötig ist. Sie hilft beim korrekten Aussprechen und beim Unterscheiden von Wörtern, die sonst gleich aussehen.

### Die drei Grundregeln der Betonung

**Wortarten nach betonter Silbe**
| Typ | Betonte Silbe | Akzentregel |
|---|---|---|
| palabras agudas | letzte Silbe | Akzent nur bei Endung auf Vokal, -n oder -s |
| palabras llanas | vorletzte Silbe | Akzent außer bei Endung auf Vokal, -n oder -s |
| palabras esdrújulas | drittletzte Silbe | immer Akzent |

### Beispiele zu den Regeln

- _El sofá es cómodo._ (Das Sofa ist bequem. (aguda mit Akzent + esdrújula))
- _El árbol está en el jardín._ (Der Baum ist im Garten. (llana mit Akzent, endet auf -l))
- _Compré una lámpara nueva._ (Ich habe eine neue Lampe gekauft. (esdrújula, immer Akzent))
- _El reloj no funciona._ (Die Uhr funktioniert nicht. (aguda ohne Akzent, endet auf -j))

### Verwendung

- **Betonte Endsilbe kennzeichnen** — _Voy a hablar con el capitán._ (Ich werde mit dem Kapitän sprechen.)
- **Wörter mit gleichem Klang unterscheiden (tilde diacrítica)** — _Sé que tú tienes tu libro._ (Ich weiß, dass du dein Buch hast.)
- **Fragewörter mit Akzent** — _¿Qué quieres? No sé qué comprar._ (Was willst du? Ich weiß nicht, was ich kaufen soll.)
- **Verbformen der Vergangenheit** — _Ayer hablé con María._ (Gestern habe ich mit María gesprochen.)

### Tilde diacrítica: gleiche Schreibung, anderer Sinn

**Wortpaare, nur durch den Akzent unterschieden**
| Ohne Akzent | Bedeutung | Mit Akzent | Bedeutung |
|---|---|---|---|
| tu | dein | tú | du |
| el | der (Artikel) | él | er |
| mi | mein | mí | mir/mich |
| si | wenn/ob | sí | ja/sich |
| se | sich | sé | ich weiß |
| te | dich/dir | té | Tee |

> ⚠️ Deutsche Muttersprachler vergessen häufig den Akzent bei den regelmäßigen Vergangenheitsformen wie 'hablé', 'comí' oder 'estudió'. Ohne Akzent ('hable', 'estudio') entsteht eine andere Form oder Zeit — 'estudio' heißt 'ich lerne', 'estudió' heißt 'er/sie lernte'.

## `preposiciones` — Preposiciones  (A2)
*Die wichtigsten Präpositionen* · Konzept: `preposiciones-a-en-de`

Präpositionen sind unveränderliche Wörter, die Beziehungen zwischen Wörtern herstellen: Ort, Zeit, Richtung, Zweck oder Zugehörigkeit. Sie sind unverzichtbar, um im Alltag anzugeben, wo etwas ist, wohin man geht oder wann etwas passiert. Im Spanischen entsprechen sie oft nicht eins zu eins den deutschen Präpositionen.

### Die wichtigsten Präpositionen

**Grundbedeutungen**
| Präposition | Bedeutung |
|---|---|
| a | zu, nach, um (Zeit/Richtung) |
| de | von, aus, über (Herkunft/Besitz) |
| en | in, auf, an (Ort) |
| con | mit |
| sin | ohne |
| por | wegen, durch, per, für |
| para | für, um zu, nach (Ziel/Zweck) |
| desde | seit, von ... an |
| hasta | bis |
| entre | zwischen |
| sobre | auf, über |
| hacia | in Richtung |

### Verwendung

- **Ort angeben (en)** — _Las llaves están en la mesa._ (Die Schlüssel sind auf dem Tisch.)
- **Richtung/Ziel (a)** — _Vamos a Madrid este fin de semana._ (Wir fahren dieses Wochenende nach Madrid.)
- **Herkunft und Besitz (de)** — _Soy de Alemania y este coche es de mi hermano._ (Ich komme aus Deutschland und dieses Auto gehört meinem Bruder.)
- **Begleitung (con / sin)** — _¿Venís con nosotros o vais sin paraguas?_ (Kommt ihr mit uns oder geht ihr ohne Regenschirm?)
- **Zeitspanne (desde ... hasta)** — _Trabajo desde las nueve hasta las cinco._ (Ich arbeite von neun bis fünf.)

### por oder para?

**Unterscheidung von por und para**
| Verwendung | Beispiel (es) | Übersetzung |
|---|---|---|
| Grund/Ursache (por) | Gracias por tu ayuda. | Danke für deine Hilfe. |
| Durch einen Ort (por) | Paseamos por el parque. | Wir spazieren durch den Park. |
| Zweck/Ziel (para) | Este regalo es para ti. | Dieses Geschenk ist für dich. |
| Frist (para) | Lo necesito para el lunes. | Ich brauche es bis Montag (Frist). |

### Verschmelzungen a + el / de + el

**Pflichtkontraktionen mit dem Artikel el**
| Kombination | Ergebnis | Beispiel |
|---|---|---|
| a + el | al | Voy al médico. |
| de + el | del | Vengo del trabajo. |

> ⚠️ Deutsche verwechseln oft por und para, weil beide 'für' bedeuten können. Merke: por nennt den Grund (por el tráfico = wegen des Verkehrs), para den Zweck oder Empfänger (para el trabajo = für die Arbeit). Außerdem sind al und del Pflicht: nie 'a el' oder 'de el' schreiben.

## `presente-indicativo-2` — Presente de Indicativo II  (A2)
*Unregelmäßige Verben im Präsens* · Konzept: `presente-indicativo`

Viele häufige spanische Verben folgen im Präsens nicht dem regelmäßigen Muster. Sie ändern den Vokal im Stamm oder haben besondere Formen. Diese Verben brauchst du täglich, denn dazu gehören querer, poder, dormir, pedir oder hacer.

### Diphthongierung: e → ie und o → ue

**Der Stammvokal ändert sich in allen Formen außer bei nosotros/vosotros.**
|  | querer (wollen) | poder (können) |
|---|---|---|
| yo | quiero | puedo |
| tú | quieres | puedes |
| él, ella, usted | quiere | puede |
| nosotros, nosotras | queremos | podemos |
| vosotros, vosotras | queréis | podéis |
| ellos, ellas, ustedes | quieren | pueden |

### Vokalwechsel e → i

**Nur bei einigen Verben auf -ir; nosotros/vosotros bleiben unverändert.**
|  | pedir (bitten) | seguir (folgen) |
|---|---|---|
| yo | pido | sigo |
| tú | pides | sigues |
| él, ella, usted | pide | sigue |
| nosotros, nosotras | pedimos | seguimos |
| vosotros, vosotras | pedís | seguís |
| ellos, ellas, ustedes | piden | siguen |

### Unregelmäßige erste Person (yo)

**Nur die yo-Form ist unregelmäßig, der Rest ist regelmäßig.**
|  | hacer (machen) | poner (setzen) | salir (hinausgehen) |
|---|---|---|---|
| yo | hago | pongo | salgo |
| tú | haces | pones | sales |
| él, ella, usted | hace | pone | sale |
| nosotros, nosotras | hacemos | ponemos | salimos |
| vosotros, vosotras | hacéis | ponéis | salís |
| ellos, ellas, ustedes | hacen | ponen | salen |

### Verwendung

- **Wunsch oder Absicht ausdrücken** — _Quiero un café con leche, por favor._ (Ich möchte einen Milchkaffee, bitte.)
- **Fähigkeit oder Möglichkeit** — _No puedo venir esta tarde._ (Ich kann heute Nachmittag nicht kommen.)
- **Um etwas bitten (im Lokal)** — _Siempre pido la tortilla de patatas._ (Ich bestelle immer die Kartoffeltortilla.)
- **Gewohnheiten und Tätigkeiten** — _Los sábados hago la compra por la mañana._ (Samstags erledige ich morgens den Einkauf.)
- **Über Uhrzeiten des Alltags sprechen** — _Salgo de casa a las ocho._ (Ich verlasse das Haus um acht Uhr.)

### Weitere häufige Sonderformen

**Verben mit doppelter Unregelmäßigkeit (yo-Form und Diphthong).**
|  | tener (haben) | venir (kommen) | decir (sagen) |
|---|---|---|---|
| yo | tengo | vengo | digo |
| tú | tienes | vienes | dices |
| él, ella, usted | tiene | viene | dice |
| nosotros, nosotras | tenemos | venimos | decimos |
| vosotros, vosotras | tenéis | venís | decís |
| ellos, ellas, ustedes | tienen | vienen | dicen |

> ⚠️ Häufiger Fehler: Der Vokalwechsel wird fälschlich auch bei nosotros und vosotros angewendet. Es heißt queremos und podéis, NICHT „quieremos" oder „puedéis". Nur in diesen beiden Formen bleibt der Stammvokal unverändert.

## `pronombres-complemento-directo` — Pronombres de Complemento Directo  (A2)
*lo, la, los, las — direkte Objektpronomen* · Konzept: `pronombres-od`

Die direkten Objektpronomen (Pronombres de Complemento Directo) ersetzen das direkte Objekt eines Satzes, um Wiederholungen zu vermeiden. Statt „Veo el coche“ sagt man „Lo veo“. Sie richten sich in Geschlecht und Zahl nach dem Substantiv, das sie ersetzen.

### Die Formen

**Direkte Objektpronomen**
| Person | Singular | Plural |
|---|---|---|
| 1. Person | me (mich) | nos (uns) |
| 2. Person | te (dich) | os (euch) |
| 3. Person maskulin | lo (ihn/es) | los (sie) |
| 3. Person feminin | la (sie/es) | las (sie) |

lo, la, los, las ersetzen sowohl Personen als auch Sachen. Das Geschlecht richtet sich nach dem ersetzten Substantiv: el libro → lo, la casa → la.

### Stellung im Satz

**Position des Pronomens**
|  | Beispiel | Übersetzung |
|---|---|---|
| Vor konjugiertem Verb | La compro. | Ich kaufe sie. |
| Am Infinitiv angehängt | Voy a comprarla. | Ich werde sie kaufen. |
| Vor der Verbalperiphrase | La voy a comprar. | Ich werde sie kaufen. |
| Am Gerundium angehängt | Estoy comprándola. | Ich kaufe sie gerade. |

### Verwendung

- **Eine Sache ersetzen** — _¿Tienes el móvil? Sí, lo tengo aquí._ (Hast du das Handy? Ja, ich habe es hier.)
- **Eine Person ersetzen** — _¿Conoces a María? Sí, la conozco bien._ (Kennst du María? Ja, ich kenne sie gut.)
- **Plural ersetzen** — _¿Compras las manzanas? Sí, las compro._ (Kaufst du die Äpfel? Ja, ich kaufe sie.)
- **Angehängt an den Infinitiv** — _Estas cartas quiero enviarlas hoy._ (Diese Briefe will ich heute abschicken.)
- **Euch ansprechen (vosotros)** — _Os espero en la puerta._ (Ich warte auf euch am Eingang.)

### Besonderheit: neutrales lo

**lo für ganze Aussagen oder Adjektive**
|  | Beispiel | Übersetzung |
|---|---|---|
| Ersetzt eine Aussage | ¿Sabes que viene? Sí, lo sé. | Weißt du, dass er kommt? Ja, ich weiß es. |
| Ersetzt ein Adjektiv | ¿Está cansada? Sí, lo está. | Ist sie müde? Ja, das ist sie. |

> ⚠️ Deutsche Muttersprachler vergessen oft, das Objekt bei bekannten Dingen durch ein Pronomen zu ersetzen, und wiederholen das Substantiv: „¿Compras el pan? Sí, compro el pan.“ ist unnatürlich. Richtig: „Sí, lo compro.“ Achte außerdem darauf, das Pronomen VOR das konjugierte Verb zu stellen, nicht dahinter wie im Deutschen: „Lo veo“, nicht „Veo lo“.

## `gerundio` — Gerundio  (A2)
*hablando, comiendo — die Verlaufsform* · Konzept: `gerundio`

Das Gerundio (auf -ando/-iendo) entspricht in etwa dem deutschen Partizip auf -end. Kombiniert mit estar bildet es die Verlaufsform (estar + gerundio) und drückt aus, dass eine Handlung gerade abläuft: estoy hablando – ich bin gerade am Sprechen.

### Bildung des Gerundio

**Regelmäßige Endungen nach Verbgruppe**
|  | Endung | Beispiel |
|---|---|---|
| -ar-Verben | -ando | hablar → hablando |
| -er-Verben | -iendo | comer → comiendo |
| -ir-Verben | -iendo | vivir → viviendo |

### Estar + Gerundio (die Verlaufsform)

**estar konjugiert + Gerundio**
|  | estar + hablando |
|---|---|
| yo | estoy hablando |
| tú | estás hablando |
| él, ella, usted | está hablando |
| nosotros, nosotras | estamos hablando |
| vosotros, vosotras | estáis hablando |
| ellos, ellas, ustedes | están hablando |

### Verwendung

- **Eine Handlung, die genau jetzt abläuft** — _No puedo hablar, estoy conduciendo._ (Ich kann nicht reden, ich fahre gerade Auto.)
- **Vorübergehende Handlung in diesem Zeitraum** — _Este mes estamos estudiando español._ (Diesen Monat lernen wir gerade Spanisch.)
- **Frage nach der aktuellen Tätigkeit** — _¿Qué estáis haciendo?_ (Was macht ihr gerade?)
- **Art und Weise (ohne estar)** — _Entró en casa cantando._ (Er kam singend nach Hause.)

### Unregelmäßige Gerundios

**Häufige unregelmäßige Formen**
| Infinitiv | Gerundio | Übersetzung |
|---|---|---|
| leer | leyendo | lesend |
| oír | oyendo | hörend |
| ir | yendo | gehend |
| dormir | durmiendo | schlafend |
| pedir | pidiendo | bittend |
| decir | diciendo | sagend |
| venir | viniendo | kommend |
| poder | pudiendo | könnend |

### Stellung der Pronomen

**Objektpronomen beim Gerundio**
| Variante | Beispiel | Übersetzung |
|---|---|---|
| angehängt | estoy leyéndolo | ich lese es gerade |
| vorangestellt | lo estoy leyendo | ich lese es gerade |

> ⚠️ Deutschsprachige benutzen die Verlaufsform oft zu häufig. Für allgemeine oder wiederkehrende Handlungen steht im Spanischen das normale Präsens, nicht estar + gerundio: 'Trabajo en Madrid' (Ich arbeite in Madrid), nicht 'Estoy trabajando en Madrid', wenn kein Bezug auf den aktuellen Moment gemeint ist. Für die Zukunft gilt das Gerundio nie: 'Mañana voy al médico', nicht 'Mañana estoy yendo'.

## `participio` — Participio  (A2)
*hablado, comido — das Partizip* · Konzept: `participio`

Das Participio (Partizip) ist eine unveränderliche Verbform, die man vor allem für zusammengesetzte Zeiten mit dem Hilfsverb 'haber' braucht (z. B. 'he hablado'). Es kann außerdem als Adjektiv dienen. In dieser Lektion geht es um die Bildung und die wichtigsten unregelmäßigen Formen.

### Bildung des Participio

**Regelmäßige Endungen nach Verbklasse**
|  | Endung | Beispiel |
|---|---|---|
| -ar-Verben | -ado | hablar → hablado |
| -er-Verben | -ido | comer → comido |
| -ir-Verben | -ido | vivir → vivido |

### Verwendung

- **Perfekt mit haber (unveränderlich)** — _He hablado con el médico esta mañana._ (Ich habe heute Morgen mit dem Arzt gesprochen.)
- **Als Adjektiv (kongruiert in Genus und Numerus)** — _La puerta está cerrada y las ventanas abiertas._ (Die Tür ist geschlossen und die Fenster sind offen.)
- **Mit estar für einen Zustand** — _El trabajo ya está terminado._ (Die Arbeit ist schon fertig.)
- **Ihr-Form (vosotros) im Perfekt** — _¿Habéis comido ya?_ (Habt ihr schon gegessen?)

### Wichtige unregelmäßige Partizipien

**Häufige unregelmäßige Formen**
| Infinitiv | Participio | Bedeutung |
|---|---|---|
| abrir | abierto | geöffnet |
| escribir | escrito | geschrieben |
| decir | dicho | gesagt |
| hacer | hecho | gemacht |
| ver | visto | gesehen |
| poner | puesto | gestellt/gelegt |
| volver | vuelto | zurückgekehrt |
| romper | roto | zerbrochen |
| morir | muerto | gestorben |

> ⚠️ Nach 'haber' bleibt das Participio immer unveränderlich – nie an das Subjekt anpassen. Falsch ist 'ellos han llegados' oder 'Ana ha comida'; richtig ist 'ellos han llegado' und 'Ana ha comido'. Nur als Adjektiv (mit ser/estar oder beim Substantiv) verändert es sich: 'las ventanas están abiertas'.

## `pronombres-reflexivos` — Pronombres Reflexivos  (A2)
*me, te, se — reflexive Verben* · Konzept: `verbos-reflexivos`

Reflexive Pronomen zeigen an, dass sich eine Handlung auf das Subjekt selbst richtet. Viele alltägliche Verben sind im Spanischen reflexiv: aufstehen, sich waschen, sich anziehen. Das Pronomen (me, te, se …) begleitet dabei immer das konjugierte Verb und richtet sich nach der Person.

### Die reflexiven Pronomen

**Formen der reflexiven Pronomen**
|  | Pronomen |
|---|---|
| yo | me |
| tú | te |
| él, ella, usted | se |
| nosotros, nosotras | nos |
| vosotros, vosotras | os |
| ellos, ellas, ustedes | se |

### Konjugation reflexiver Verben

**levantarse (aufstehen), ducharse (duschen), acostarse (sich hinlegen, o→ue)**
|  | levantarse | ducharse | acostarse |
|---|---|---|---|
| yo | me levanto | me ducho | me acuesto |
| tú | te levantas | te duchas | te acuestas |
| él, ella, usted | se levanta | se ducha | se acuesta |
| nosotros, nosotras | nos levantamos | nos duchamos | nos acostamos |
| vosotros, vosotras | os levantáis | os ducháis | os acostáis |
| ellos, ellas, ustedes | se levantan | se duchan | se acuestan |

### Stellung des Pronomens

**Bei Infinitiv und Gerundium kann das Pronomen angehängt werden**
|  | Beispiel |
|---|---|
| konjugiertes Verb (davor) | Me lavo las manos. |
| Infinitiv (angehängt oder davor) | Voy a ducharme. / Me voy a duchar. |
| Gerundium (angehängt oder davor) | Estoy vistiéndome. / Me estoy vistiendo. |

### Verwendung

- **Tägliche Routine** — _Me levanto a las siete y me ducho enseguida._ (Ich stehe um sieben auf und dusche sofort.)
- **Körperteile und Kleidung (mit Artikel, nicht Possessivpronomen)** — _Se lava los dientes después de comer._ (Er/Sie putzt sich nach dem Essen die Zähne.)
- **Gefühle und Zustandsänderungen** — _Mi hermana se enfada cuando llegamos tarde._ (Meine Schwester ärgert sich, wenn wir zu spät kommen.)
- **Gegenseitigkeit (im Plural)** — _Mi novio y yo nos vemos todos los días._ (Mein Freund und ich sehen uns jeden Tag.)

### Verben mit Bedeutungswechsel

**Manche Verben ändern mit dem Pronomen ihre Bedeutung**
| ohne Pronomen | mit Pronomen |
|---|---|
| ir (gehen) | irse (weggehen) |
| dormir (schlafen) | dormirse (einschlafen) |
| llamar (rufen, anrufen) | llamarse (heißen) |
| poner (stellen, legen) | ponerse (sich anziehen; werden) |

> ⚠️ Deutsche vergessen oft, dass bei Körperteilen und Kleidung der bestimmte Artikel steht, nicht das Possessivpronomen. Es heißt 'Me lavo las manos' (nicht 'Me lavo mis manos') – das Reflexivpronomen 'me' zeigt bereits an, dass es die eigenen Hände sind.

## `futuro` — Futuro  (A2)
*hablaré — das einfache Futur* · Konzept: `futuro-simple`

Das Futuro simple drückt zukünftige Handlungen und Vorhersagen aus und dient auch für Vermutungen über die Gegenwart. Es wird gebildet, indem an den vollständigen Infinitiv einheitliche Endungen angehängt werden – für alle drei Konjugationsgruppen dieselben.

### Bildung: Infinitiv + Endung

**Endungen des Futuro simple (gleich für -ar, -er, -ir)**
|  | Endung | hablar | comer | vivir |
|---|---|---|---|---|
| yo | -é | hablaré | comeré | viviré |
| tú | -ás | hablarás | comerás | vivirás |
| él, ella, usted | -á | hablará | comerá | vivirá |
| nosotros, nosotras | -emos | hablaremos | comeremos | viviremos |
| vosotros, vosotras | -éis | hablaréis | comeréis | viviréis |
| ellos, ellas, ustedes | -án | hablarán | comerán | vivirán |

### Verwendung

- **Zukünftige Handlungen** — _Mañana hablaré con el médico._ (Morgen werde ich mit dem Arzt sprechen.)
- **Vorhersagen** — _El fin de semana lloverá en el norte._ (Am Wochenende wird es im Norden regnen.)
- **Vermutung über die Gegenwart** — _¿Qué hora es? Serán las tres._ (Wie spät ist es? Es wird wohl drei Uhr sein.)
- **Versprechen** — _Te llamaré cuando llegue a casa._ (Ich rufe dich an, wenn ich zu Hause ankomme.)

### Unregelmäßige Stämme

**Diese Verben ändern den Stamm, behalten aber dieselben Endungen**
| Infinitiv | Stamm | Beispiel (yo) |
|---|---|---|
| tener | tendr- | tendré |
| poner | pondr- | pondré |
| salir | saldr- | saldré |
| venir | vendr- | vendré |
| poder | podr- | podré |
| saber | sabr- | sabré |
| haber | habr- | habré |
| hacer | har- | haré |
| decir | dir- | diré |
| querer | querr- | querré |

> ⚠️ Deutsche Muttersprachler greifen für die Zukunft oft automatisch zum Futuro, obwohl das Spanische im Alltag meist 'ir a + Infinitiv' oder das Präsens verwendet: 'Mañana voy a hablar con él' oder 'Mañana hablo con él' klingt natürlicher als 'hablaré'. Das Futuro simple wirkt oft förmlicher oder betont Vorhersagen und Vermutungen.

## `apocope` — Apócope  (A2)
*buen, gran, primer — verkürzte Formen* · Konzept: `apocope`

Als Apócope bezeichnet man die Verkürzung bestimmter Wörter, wenn sie direkt vor einem Substantiv stehen. So wird aus bueno ein buen und aus grande ein gran. Diese Formen klingen natürlicher und werden im Alltag ständig gebraucht.

### Adjektive mit Apócope vor männlichem Singular

**Diese Adjektive verlieren das -o vor einem männlichen Substantiv im Singular.**
| Vollform | Verkürzt | Beispiel |
|---|---|---|
| bueno | buen | un buen amigo |
| malo | mal | un mal día |
| primero | primer | el primer piso |
| tercero | tercer | el tercer capítulo |
| uno | un | un libro |
| alguno | algún | algún problema |
| ninguno | ningún | ningún error |

### grande und weitere Sonderfälle

**grande verkürzt sich vor männlichen UND weiblichen Substantiven im Singular.**
| Vollform | Verkürzt | Beispiel |
|---|---|---|
| grande | gran | un gran hombre / una gran mujer |
| ciento | cien | cien euros |
| cualquiera | cualquier | cualquier persona |
| santo | san | san Pedro |

### Verwendung

- **Eigenschaft vor dem Substantiv** — _Es un buen profesor._ (Er ist ein guter Lehrer.)
- **Ordnungszahl vor dem Substantiv** — _Vivo en el primer piso._ (Ich wohne im ersten Stock.)
- **gran mit Bedeutungswechsel (großartig)** — _Madrid es una gran ciudad._ (Madrid ist eine großartige Stadt.)
- **Unbestimmte Menge** — _No tengo ningún plan para hoy._ (Ich habe keinen Plan für heute.)
- **Zahl vor dem Substantiv** — _Hay cien personas en la sala._ (Es sind hundert Personen im Saal.)

### Wichtige Ausnahmen

**Keine Verkürzung in diesen Fällen.**
| Regel | Beispiel | Übersetzung |
|---|---|---|
| Adjektiv steht NACH dem Substantiv | un día bueno | ein guter Tag |
| Vor weiblichem Substantiv (außer grande) | una buena idea | eine gute Idee |
| Im Plural | unos buenos amigos | gute Freunde |
| san wird nicht vor Do-/To- verkürzt | Santo Domingo, Santo Tomás | (Ortsname / Heiliger) |

> ⚠️ Deutschsprachige verwenden die Vollform oft an der falschen Stelle: Vor dem männlichen Substantiv muss verkürzt werden. Also 'un buen coche' (nicht 'un bueno coche'), aber 'un coche bueno', wenn das Adjektiv nachgestellt ist.

## `comparativos-superlativos` — Comparativos y Superlativos  (A2)
*más que, el más — vergleichen und steigern* · Konzept: `comparativos`

Mit den comparativos vergleichst du zwei Dinge oder Personen (mehr, weniger oder gleich), mit den superlativos hebst du eines aus einer Gruppe hervor (der/die/das ...ste). Beides brauchst du täglich, um Preise, Eigenschaften oder Vorlieben zu beschreiben.

### Die drei Vergleichsformen

**Grundstrukturen des Vergleichs**
| Vergleich | Struktur | Beispiel |
|---|---|---|
| Überlegenheit (mehr) | más + Adjektiv + que | más alto que |
| Unterlegenheit (weniger) | menos + Adjektiv + que | menos caro que |
| Gleichheit | tan + Adjektiv + como | tan rápido como |

### Der Superlativ

**Bildung des Superlativs mit bestimmtem Artikel**
|  | Form | Beispiel |
|---|---|---|
| Höchststufe (+) | el/la/los/las + más + Adjektiv | el más caro |
| Tiefststufe (−) | el/la/los/las + menos + Adjektiv | la menos cara |
| mit Bezugsgruppe | ... de ... | el más caro de la tienda |

### Verwendung

- **Zwei Dinge vergleichen (mehr)** — _Este piso es más grande que el nuestro._ (Diese Wohnung ist größer als unsere.)
- **Zwei Dinge vergleichen (weniger)** — _El tren es menos rápido que el avión._ (Der Zug ist weniger schnell als das Flugzeug.)
- **Gleichheit ausdrücken** — _Mi hermana es tan simpática como tú._ (Meine Schwester ist genauso nett wie du.)
- **Etwas hervorheben** — _Es el restaurante más caro de la ciudad._ (Es ist das teuerste Restaurant der Stadt.)
- **Mengen vergleichen** — _Vosotros tenéis más libros que nosotros._ (Ihr habt mehr Bücher als wir.)

### Unregelmäßige Formen

**Adjektive mit eigener Vergleichs- und Superlativform**
| Adjektiv | Komparativ | Superlativ |
|---|---|---|
| bueno (gut) | mejor | el mejor |
| malo (schlecht) | peor | el peor |
| grande (groß/älter) | mayor | el mayor |
| pequeño (klein/jünger) | menor | el menor |

> ⚠️ Im Vergleich heißt „als“ immer que, nicht como. Deutsche sagen oft fälschlich „más grande como“ (nach dem deutschen „so groß wie“). Richtig: „más grande que“. Como benutzt du nur in der Gleichheit: „tan grande como“.

## `pronombres-complemento-indirecto` — Pronombres Átonos de Complemento Indirecto  (B1)
*me, te, le — indirekte Objektpronomen* · Konzept: `pronombres-oi`

Die unbetonten indirekten Objektpronomen ersetzen die Person oder Sache, die den Empfänger einer Handlung darstellt — also wem etwas gegeben, gesagt oder geschickt wird. Sie antworten auf die Frage '¿A quién?'. Anders als beim direkten Objekt gibt es hier für die dritte Person nur eine Form: le beziehungsweise les.

### Die Formen

**Unbetonte indirekte Objektpronomen**
|  | Pronomen |
|---|---|
| yo | me |
| tú | te |
| él, ella, usted | le |
| nosotros, nosotras | nos |
| vosotros, vosotras | os |
| ellos, ellas, ustedes | les |

### Stellung im Satz

**Position des Pronomens**
|  | Beispiel |
|---|---|
| Vor konjugiertem Verb | Te escribo mañana. |
| Am Infinitiv angehängt | Voy a escribirte. |
| Am Gerundium angehängt | Estoy escribiéndote. |
| Am bejahten Imperativ angehängt | Escríbeme. |

### Verwendung

- **Empfänger einer Handlung (geben, schicken)** — _Le doy el libro a mi hermano._ (Ich gebe meinem Bruder das Buch.)
- **Verben des Sagens und Kommunizierens** — _¿Os cuento lo que pasó ayer?_ (Soll ich euch erzählen, was gestern passiert ist?)
- **Mit Verben wie gustar, doler, interesar** — _A mí me gusta el café solo._ (Mir gefällt schwarzer Kaffee.)
- **Verdopplung mit betontem 'a + Person'** — _A María le encanta viajar._ (María liebt es zu reisen.)

### Kombination mit direktem Objekt: le/les wird zu se

**Zwei Pronomen zusammen**
|  | Beispiel | Erklärung |
|---|---|---|
| le + lo/la | Se lo doy. | Nicht 'le lo': le wird zu se |
| les + los/las | Se las mando. | Nicht 'les las': les wird zu se |

> ⚠️ Deutsche Muttersprachler vergessen oft die 'redundante' Verdopplung: Auch wenn das indirekte Objekt als 'a + Person' bereits genannt ist, muss le/les zusätzlich stehen. Es heißt 'A Juan le regalo flores', nicht 'A Juan regalo flores'.

## `preterito-indefinido` — Pretérito Indefinido  (B1)
*hablé — die abgeschlossene Vergangenheit* · Konzept: `indefinido`

Das Pretérito Indefinido bezeichnet abgeschlossene Handlungen in der Vergangenheit, die zu einem bestimmten Zeitpunkt geschehen und beendet sind. Man braucht es, um zu erzählen, was passiert ist: Ereignisse, Abfolgen, einmalige Aktionen. Typische Signalwörter sind ayer, anoche, el año pasado, en 2010 oder de repente.

### Regelmäßige Endungen

**Endungen der drei Konjugationsklassen**
|  | -ar (hablar) | -er (comer) | -ir (vivir) |
|---|---|---|---|
| yo | hablé | comí | viví |
| tú | hablaste | comiste | viviste |
| él, ella, usted | habló | comió | vivió |
| nosotros, nosotras | hablamos | comimos | vivimos |
| vosotros, vosotras | hablasteis | comisteis | vivisteis |
| ellos, ellas, ustedes | hablaron | comieron | vivieron |

### Verwendung

- **Einmalige abgeschlossene Handlung** — _Ayer compré un coche nuevo._ (Gestern kaufte ich ein neues Auto.)
- **Abfolge von Ereignissen** — _Entré, dejé las llaves y me senté._ (Ich kam herein, legte die Schlüssel ab und setzte mich.)
- **Handlung mit bestimmtem Zeitraum** — _Viví en Madrid tres años._ (Ich lebte drei Jahre in Madrid.)
- **Datierter historischer Fakt** — _La guerra terminó en 1939._ (Der Krieg endete 1939.)
- **Plötzliche Unterbrechung** — _De repente sonó el teléfono._ (Plötzlich klingelte das Telefon.)

### Wichtige unregelmäßige Verben

**Häufige unregelmäßige Formen (eigener Stamm, endungslose Betonung)**
|  | ser/ir | estar | tener | hacer | poder |
|---|---|---|---|---|---|
| yo | fui | estuve | tuve | hice | pude |
| tú | fuiste | estuviste | tuviste | hiciste | pudiste |
| él, ella, usted | fue | estuvo | tuvo | hizo | pudo |
| nosotros, nosotras | fuimos | estuvimos | tuvimos | hicimos | pudimos |
| vosotros, vosotras | fuisteis | estuvisteis | tuvisteis | hicisteis | pudisteis |
| ellos, ellas, ustedes | fueron | estuvieron | tuvieron | hicieron | pudieron |

> ⚠️ Verwechsle das Indefinido nicht mit dem Imperfecto: Für abgeschlossene, punktuelle Ereignisse steht das Indefinido (Ayer comí paella), für Gewohnheiten, Beschreibungen oder Hintergrund das Imperfecto (Antes comía paella los domingos). Deutsche greifen oft fälschlich zum Imperfecto, weil im Deutschen beides mit dem Präteritum ausgedrückt wird.

## `preterito-imperfecto` — Pretérito Imperfecto de Indicativo  (B1)
*hablaba — die beschreibende Vergangenheit* · Konzept: `imperfecto`

Das Pretérito Imperfecto beschreibt die Vergangenheit: gewohnheitsmäßige Handlungen, andauernde Zustände, Umstände und Beschreibungen. Es sagt nicht, wann etwas begann oder endete, sondern wie es war. Man braucht es für Kulissen, Wiederholungen und Hintergründe – oft im Kontrast zum Pretérito Indefinido.

### Regelmäßige Formen

**Verben auf -ar, -er, -ir**
|  | hablar | comer | vivir |
|---|---|---|---|
| yo | hablaba | comía | vivía |
| tú | hablabas | comías | vivías |
| él, ella, usted | hablaba | comía | vivía |
| nosotros, nosotras | hablábamos | comíamos | vivíamos |
| vosotros, vosotras | hablabais | comíais | vivíais |
| ellos, ellas, ustedes | hablaban | comían | vivían |

Die -er- und -ir-Verben haben identische Endungen. Alle Formen von -ía tragen einen Akzent auf dem i. Bei -ar liegt der Akzent nur in der nosotros-Form (hablábamos).

### Verwendung

- **Gewohnheiten in der Vergangenheit** — _De niño jugaba al fútbol todos los días._ (Als Kind spielte ich jeden Tag Fußball.)
- **Beschreibung von Umständen und Kulissen** — _Era de noche y llovía mucho._ (Es war Nacht und es regnete stark.)
- **Andauernde Handlung, unterbrochen von einer anderen** — _Cenábamos cuando sonó el teléfono._ (Wir aßen gerade zu Abend, als das Telefon klingelte.)
- **Alter, Uhrzeit und Zustände in der Vergangenheit** — _Eran las tres y tenía mucho sueño._ (Es war drei Uhr und ich war sehr müde.)
- **Höfliche oder abgeschwächte Bitten** — _Quería preguntarte una cosa._ (Ich wollte dich etwas fragen.)

### Unregelmäßige Verben

**Nur drei Verben sind im Imperfecto unregelmäßig**
|  | ser | ir | ver |
|---|---|---|---|
| yo | era | iba | veía |
| tú | eras | ibas | veías |
| él, ella, usted | era | iba | veía |
| nosotros, nosotras | éramos | íbamos | veíamos |
| vosotros, vosotras | erais | ibais | veíais |
| ellos, ellas, ustedes | eran | iban | veían |

> ⚠️ Deutsche Muttersprachler wählen oft das Imperfecto, weil das deutsche Präteritum ("ich spielte") es nahelegt. Im Spanischen entscheidet aber die Perspektive: eine abgeschlossene Einzelhandlung braucht das Indefinido (Ayer jugué al fútbol), eine Gewohnheit oder Beschreibung das Imperfecto (De niño jugaba al fútbol). Nicht am deutschen Zeitwort festmachen, sondern fragen: einmalig/abgeschlossen oder wiederholt/beschreibend?

## `contraste-indefinido-imperfecto` — Contraste Indefinido / Imperfecto  (B1)
*Wann welche Vergangenheit?* · Konzept: `indefinido-vs-imperfecto`

Beide Zeitformen erzählen von der Vergangenheit, aber aus unterschiedlicher Perspektive. Das Indefinido nennt abgeschlossene, punktuelle Ereignisse, die die Handlung vorantreiben. Das Imperfecto beschreibt den Rahmen: Umstände, Gewohnheiten, Beschreibungen und andauernde Zustände. Wer beide unterscheidet, erzählt im Alltag klar und natürlich.

### Grundunterscheidung

**Wann welche Vergangenheit?**
| Funktion | Indefinido | Imperfecto |
|---|---|---|
| Ereignis | abgeschlossen, punktuell | andauernd, im Verlauf |
| Zeitrahmen | begrenzt / abgeschlossen | unbegrenzt / offen |
| Wiederholung | einmalig / gezählt | gewohnheitsmäßig |
| Rolle in der Erzählung | treibt die Handlung voran | beschreibt den Hintergrund |

### Typische Signalwörter

**Marcadores temporales**
|  | Beispiel | Übersetzung |
|---|---|---|
| Indefinido | ayer, anoche, el lunes, en 2010, una vez, de repente | gestern, gestern Nacht, am Montag, 2010, einmal, plötzlich |
| Imperfecto | antes, siempre, todos los días, mientras, normalmente | früher, immer, jeden Tag, während, normalerweise |

### Verwendung

- **Abgeschlossenes Ereignis (Indefinido)** — _Ayer comí en un restaurante italiano._ (Gestern aß ich in einem italienischen Restaurant.)
- **Beschreibung / Umstände (Imperfecto)** — _El restaurante era pequeño y estaba lleno._ (Das Restaurant war klein und war voll.)
- **Gewohnheit in der Vergangenheit (Imperfecto)** — _De niños íbamos a la playa todos los veranos._ (Als Kinder gingen wir jeden Sommer ans Meer.)
- **Handlung unterbricht Hintergrund (beide)** — _Mientras cenábamos, sonó el teléfono._ (Während wir zu Abend aßen, klingelte das Telefon.)
- **Uhrzeit und Alter (Imperfecto)** — _Eran las tres cuando llegasteis a casa._ (Es war drei Uhr, als ihr nach Hause kamt.)

### Verben mit Bedeutungswechsel

**Manche Verben ändern die Nuance je nach Zeitform**
| Verb | Imperfecto | Indefinido |
|---|---|---|
| saber | sabía = wusste (Zustand) | supe = erfuhr (Moment) |
| conocer | conocía = kannte | conocí = lernte kennen |
| querer | quería = wollte | quise = versuchte / quiso no = weigerte sich |
| poder | podía = konnte (fähig sein) | pude = schaffte es (in dem Moment) |

> ⚠️ Deutsche übertragen oft das eine deutsche Präteritum eins zu eins und wählen für Beschreibungen fälschlich das Indefinido. 'Das Wetter war schön' ist 'Hacía buen tiempo' (Zustand, Imperfecto), nicht 'Hizo buen tiempo'. Faustregel: Beschreibung und Rahmen → Imperfecto; das, was dann passierte → Indefinido.

## `el-vs-lo` — Diferencia entre el y lo  (B1)
*el vs. lo — Artikel oder Neutrum?* · Konzept: `—`

Sowohl "el" als auch "lo" stehen vor anderen Wörtern, sind aber grundverschieden: "el" ist der bestimmte Artikel für männliche Substantive im Singular. "lo" ist der sogenannte Neutrumartikel und steht nie vor einem konkreten Substantiv, sondern vor Adjektiven, Adverbien oder Relativsätzen und macht daraus einen abstrakten Begriff.

### Überblick der Formen

**el vs. lo im Vergleich**
|  | el | lo |
|---|---|---|
| Wortart | bestimmter Artikel (maskulin Sg.) | Neutrumartikel |
| steht vor | männlichem Substantiv | Adjektiv, Adverb, Relativsatz |
| Genus/Numerus | hat Plural: los | unveränderlich, kein Plural |
| Beispiel | el libro | lo importante |

### Konstruktionen mit lo

**Typische Muster mit lo**
|  | Konstruktion | Bedeutung |
|---|---|---|
| lo + Adjektiv | lo bueno | das Gute |
| lo + Adverb | lo rápido | wie schnell / das Schnelle |
| lo que | lo que dices | das, was du sagst |
| lo de | lo de ayer | die Sache von gestern |
| lo más/menos + Adj. | lo más pronto posible | so bald wie möglich |

### Verwendung

- **el als Artikel vor männlichem Substantiv** — _El coche está en el garaje._ (Das Auto steht in der Garage.)
- **lo + Adjektiv für einen abstrakten Begriff** — _Lo difícil es empezar._ (Das Schwierige ist der Anfang.)
- **lo que als Relativpronomen ohne Bezugswort** — _No entiendo lo que quieres decir._ (Ich verstehe nicht, was du sagen willst.)
- **lo de für eine bekannte Angelegenheit** — _¿Sabéis algo de lo de la reunión?_ (Wisst ihr etwas über die Sache mit dem Treffen?)
- **lo + Adjektiv/Adverb zur Betonung des Grades** — _No sabes lo cansado que estoy._ (Du weißt nicht, wie müde ich bin.)

### Besondere Fälle

**lo mit veränderlichem Adjektiv im Gradausdruck**
|  | Beispiel | Deutsch |
|---|---|---|
| Adjektiv angeglichen | No te imaginas lo contentas que están. | Du ahnst nicht, wie zufrieden sie (fem. Pl.) sind. |
| Adverb unverändert | Me sorprende lo bien que cocináis. | Mich überrascht, wie gut ihr kocht. |

> ⚠️ Deutschsprachige verwechseln "lo" oft mit dem bestimmten Artikel und sagen fälschlich "lo libro". Vor einem Substantiv steht immer "el" (el libro), nie "lo". "lo" gibt es nur vor Adjektiven, Adverbien oder mit "que"/"de" — und niemals im Plural.

## `imperativo` — Imperativo  (B1)
*¡habla! — der Imperativ* · Konzept: `imperativo-afirmativo`

Der Imperativo (Befehlsform) dient dazu, Aufforderungen, Befehle, Bitten, Anweisungen oder Ratschläge auszudrücken. Im Spanischen gibt es eigene bejahende Formen für tú, usted, nosotros, vosotros und ustedes. Die verneinten Formen werden mit dem Subjuntivo gebildet.

### Bejahter Imperativ: regelmäßige Formen

**Bejahte Formen von hablar, comer, vivir**
|  | hablar | comer | vivir |
|---|---|---|---|
| tú | habla | come | vive |
| usted | hable | coma | viva |
| nosotros, nosotras | hablemos | comamos | vivamos |
| vosotros, vosotras | hablad | comed | vivid |
| ustedes | hablen | coman | vivan |

### Verneinter Imperativ

**Verneinte Formen (mit Subjuntivo gebildet)**
|  | hablar | comer | vivir |
|---|---|---|---|
| tú | no hables | no comas | no vivas |
| usted | no hable | no coma | no viva |
| nosotros, nosotras | no hablemos | no comamos | no vivamos |
| vosotros, vosotras | no habléis | no comáis | no viváis |
| ustedes | no hablen | no coman | no vivan |

### Verwendung

- **Direkter Befehl / Aufforderung** — _¡Cierra la puerta, por favor!_ (Mach bitte die Tür zu!)
- **Anweisung oder Rezept** — _Añadid dos huevos y mezclad bien._ (Gebt zwei Eier dazu und mischt gut.)
- **Ratschlag geben** — _Descansa un poco, tienes mala cara._ (Ruh dich ein bisschen aus, du siehst schlecht aus.)
- **Höfliche Bitte (usted)** — _Pase y siéntese, por favor._ (Kommen Sie herein und setzen Sie sich, bitte.)
- **Etwas verbieten (verneint)** — _No toques eso, está caliente._ (Fass das nicht an, es ist heiß.)

### Unregelmäßige Formen (tú, bejaht)

**Häufige unregelmäßige tú-Formen**
| Verb | tú (bejaht) | Beispiel |
|---|---|---|
| decir | di | Dime la verdad. |
| hacer | haz | Haz los deberes. |
| ir | ve | Ve a casa. |
| poner | pon | Pon la mesa. |
| salir | sal | Sal de aquí. |
| ser | sé | Sé amable. |
| tener | ten | Ten paciencia. |
| venir | ven | Ven conmigo. |

### Pronomen beim Imperativ

**Stellung der Pronomen**
| Form | Stellung | Beispiel |
|---|---|---|
| bejaht | angehängt (ein Wort) | Dámelo. (Gib es mir.) |
| verneint | davor, getrennt | No me lo des. (Gib es mir nicht.) |

> ⚠️ Deutsche Muttersprachler verwenden häufig fälschlich die bejahte Form auch für die Verneinung: Nicht »no habla«, sondern »no hables«. Der verneinte Imperativ wird immer mit dem Subjuntivo gebildet — auch bei tú und vosotros (no comas, no comáis), wo sich die Endungen deutlich von den bejahten Formen (come, comed) unterscheiden.

## `condicional-simple` — Condicional Simple  (B1)
*hablaría — der Konditional* · Konzept: `condicional-simple`

Der Condicional Simple drückt Höflichkeit, Wünsche, Ratschläge und hypothetische Handlungen aus. Er entspricht oft dem deutschen 'würde' plus Infinitiv. Man verwendet ihn auch, um über die Zukunft aus vergangener Sicht zu sprechen.

### Bildung der regelmäßigen Formen

An den vollständigen Infinitiv (-ar, -er, -ir) werden für alle drei Konjugationen dieselben Endungen angehängt: -ía, -ías, -ía, -íamos, -íais, -ían.

**Regelmäßige Konjugation: hablar, comer, vivir**
|  | hablar | comer | vivir |
|---|---|---|---|
| yo | hablaría | comería | viviría |
| tú | hablarías | comerías | vivirías |
| él, ella, usted | hablaría | comería | viviría |
| nosotros, nosotras | hablaríamos | comeríamos | viviríamos |
| vosotros, vosotras | hablaríais | comeríais | viviríais |
| ellos, ellas, ustedes | hablarían | comerían | vivirían |

### Verwendung

- **Höfliche Bitte oder Wunsch** — _¿Podrías ayudarme con esto?_ (Könntest du mir dabei helfen?)
- **Ratschlag geben** — _Yo que tú, hablaría con el jefe._ (An deiner Stelle würde ich mit dem Chef sprechen.)
- **Hypothetische Handlung** — _Con más tiempo, viajaríamos por toda España._ (Mit mehr Zeit würden wir durch ganz Spanien reisen.)
- **Zukunft aus vergangener Sicht** — _Dijo que vendría mañana._ (Er sagte, dass er morgen kommen würde.)
- **Vermutung über die Vergangenheit** — _Serían las tres cuando llegó._ (Es war wohl drei Uhr, als er ankam.)

### Unregelmäßige Stämme

Dieselben Verben, die im Futuro einen unregelmäßigen Stamm haben, sind es auch im Condicional. Die Endungen bleiben immer regelmäßig.

**Häufige unregelmäßige Stämme (yo-Form)**
| Infinitiv | Stamm | Beispiel (yo) |
|---|---|---|
| tener | tendr- | tendría |
| poder | podr- | podría |
| poner | pondr- | pondría |
| salir | saldr- | saldría |
| venir | vendr- | vendría |
| hacer | har- | haría |
| decir | dir- | diría |
| querer | querr- | querría |
| saber | sabr- | sabría |
| haber | habr- | habría |

> ⚠️ Deutsche verwechseln oft Condicional und Pretérito Imperfecto, weil das 'r' entscheidet: 'comía' heißt 'ich aß / ich habe gegessen', 'comería' heißt 'ich würde essen'. Das 'r' vor der Endung darf nie fehlen.

## `preterito-perfecto-compuesto` — Pretérito Perfecto Compuesto  (B2)
*he hablado — das zusammengesetzte Perfekt* · Konzept: `perfecto`

Das Pretérito Perfecto Compuesto beschreibt abgeschlossene Handlungen mit Bezug zur Gegenwart oder innerhalb eines noch nicht beendeten Zeitraums (heute, diese Woche, in meinem Leben). Es wird mit dem Präsens von haber plus Partizip gebildet. In Spanien ist es sehr gebräuchlich.

### Bildung: haber im Präsens + Partizip

**Präsens von haber als Hilfsverb**
|  | haber |
|---|---|
| yo | he |
| tú | has |
| él, ella, usted | ha |
| nosotros, nosotras | hemos |
| vosotros, vosotras | habéis |
| ellos, ellas, ustedes | han |

**Beispielkonjugation mit hablar, comer, vivir**
|  | hablar | comer | vivir |
|---|---|---|---|
| yo | he hablado | he comido | he vivido |
| tú | has hablado | has comido | has vivido |
| él, ella, usted | ha hablado | ha comido | ha vivido |
| nosotros, nosotras | hemos hablado | hemos comido | hemos vivido |
| vosotros, vosotras | habéis hablado | habéis comido | habéis vivido |
| ellos, ellas, ustedes | han hablado | han comido | han vivido |

### Verwendung

- **Handlung in noch nicht beendetem Zeitraum** — _Esta mañana he desayunado en casa._ (Heute Morgen habe ich zu Hause gefrühstückt.)
- **Vergangenes mit Gegenwartsbezug** — _Todavía no he terminado el informe._ (Ich habe den Bericht noch nicht fertiggestellt.)
- **Lebenserfahrung (ohne Zeitangabe)** — _¿Alguna vez has estado en Sevilla?_ (Warst du schon einmal in Sevilla?)
- **Ganz kürzlich Geschehenes** — _Acabas de llegar y ya has roto algo._ (Du bist gerade angekommen und hast schon etwas kaputt gemacht.)

### Unregelmäßige Partizipien

**Häufige unregelmäßige Partizipien**
| Infinitiv | Partizip |
|---|---|
| abrir | abierto |
| decir | dicho |
| escribir | escrito |
| hacer | hecho |
| poner | puesto |
| ver | visto |
| volver | vuelto |
| romper | roto |
| morir | muerto |

> ⚠️ Das Partizip verändert sich hier nie: Es bleibt immer auf -o und richtet sich nicht nach Geschlecht oder Zahl des Subjekts. Falsch ist »Ana ha llegada«, richtig ist »Ana ha llegado«. Außerdem darf zwischen haber und Partizip nichts stehen — nicht »he no comido«, sondern »no he comido«.

## `preterito-pluscuamperfecto` — Pretérito Pluscuamperfecto  (B2)
*había hablado — die Vorvergangenheit* · Konzept: `pluscuamperfecto`

Das Pretérito Pluscuamperfecto beschreibt eine Handlung, die vor einem anderen Ereignis in der Vergangenheit bereits abgeschlossen war. Es entspricht dem deutschen Plusquamperfekt und wird mit dem Imperfecto von 'haber' plus Partizip gebildet.

### Bildung: haber (Imperfecto) + Partizip

**Konjugation von 'haber' im Imperfecto mit Beispielpartizip 'hablado'**
|  | haber | Beispiel |
|---|---|---|
| yo | había | había hablado |
| tú | habías | habías hablado |
| él, ella, usted | había | había hablado |
| nosotros, nosotras | habíamos | habíamos hablado |
| vosotros, vosotras | habíais | habíais hablado |
| ellos, ellas, ustedes | habían | habían hablado |

### Regelmäßige Partizipendungen

**Partizipbildung nach Verbgruppe**
|  | Endung | Beispiel |
|---|---|---|
| -ar-Verben | -ado | hablar → hablado |
| -er-Verben | -ido | comer → comido |
| -ir-Verben | -ido | vivir → vivido |

### Verwendung

- **Handlung vor einer anderen Vergangenheitshandlung** — _Cuando llegué, ellos ya habían cenado._ (Als ich ankam, hatten sie schon zu Abend gegessen.)
- **Erstmalige Erfahrung in der Vergangenheit** — _Nunca había estado en Sevilla antes de aquel verano._ (Ich war vor jenem Sommer noch nie in Sevilla gewesen.)
- **Erklärung eines vergangenen Zustands** — _No pude entrar porque había perdido las llaves._ (Ich konnte nicht hinein, weil ich die Schlüssel verloren hatte.)
- **In indirekter Rede** — _Me dijo que ya había terminado el informe._ (Er sagte mir, dass er den Bericht schon fertiggestellt hatte.)

### Unregelmäßige Partizipien

**Häufige unregelmäßige Partizipien**
| Infinitiv | Partizip | Beispiel |
|---|---|---|
| abrir | abierto | había abierto |
| decir | dicho | había dicho |
| escribir | escrito | había escrito |
| hacer | hecho | había hecho |
| poner | puesto | había puesto |
| ver | visto | había visto |
| volver | vuelto | había vuelto |
| romper | roto | había roto |

> ⚠️ Zwischen 'haber' und dem Partizip darf nichts stehen. Pronomen kommen VOR 'haber', nicht dazwischen: richtig ist 'ya me lo había dicho', falsch 'había me lo dicho'. Das Partizip bleibt im Pluscuamperfecto immer unverändert auf -o und richtet sich nie nach Geschlecht oder Zahl.

## `subjuntivo-presente` — Subjuntivo (Presente)  (B2)
*Der Subjuntivo im Präsens* · Konzept: `subjuntivo-presente`

Der Presente de Subjuntivo drückt keine reine Tatsache aus, sondern Wunsch, Zweifel, Gefühl, Wertung oder Notwendigkeit. Er steht meist in Nebensätzen nach Auslösern wie 'querer que', 'es importante que' oder 'ojalá'. Er ist zentral für nuancierte, natürliche Kommunikation auf Spanisch.

### Bildung: regelmäßige Formen

Man geht von der 1. Person Singular des Indikativs Präsens aus, streicht das -o und hängt die Subjuntivo-Endungen an. Verben auf -ar bekommen -e-Endungen, Verben auf -er/-ir bekommen -a-Endungen ("Vokaltausch").

**Regelmäßige Endungen: hablar, comer, vivir**
|  | hablar | comer | vivir |
|---|---|---|---|
| yo | hable | coma | viva |
| tú | hables | comas | vivas |
| él, ella, usted | hable | coma | viva |
| nosotros, nosotras | hablemos | comamos | vivamos |
| vosotros, vosotras | habléis | comáis | viváis |
| ellos, ellas, ustedes | hablen | coman | vivan |

### Unregelmäßige Stämme aus dem Indikativ

Ist die 1. Person Singular Indikativ unregelmäßig, überträgt sich diese Unregelmäßigkeit auf alle Personen des Subjuntivo: tengo → tenga, hago → haga, digo → diga, salgo → salga, conozco → conozca.

**tener und hacer im Presente de Subjuntivo**
|  | tener | hacer |
|---|---|---|
| yo | tenga | haga |
| tú | tengas | hagas |
| él, ella, usted | tenga | haga |
| nosotros, nosotras | tengamos | hagamos |
| vosotros, vosotras | tengáis | hagáis |
| ellos, ellas, ustedes | tengan | hagan |

### Verwendung

- **Wunsch oder Wille (querer que, esperar que)** — _Quiero que vengas a la fiesta._ (Ich will, dass du zur Party kommst.)
- **Unpersönliche Wertung (es importante que, es necesario que)** — _Es importante que estudiéis todos los días._ (Es ist wichtig, dass ihr jeden Tag lernt.)
- **Gefühl (me alegro de que, temer que)** — _Me alegro de que estés aquí._ (Ich freue mich, dass du hier bist.)
- **Zweifel oder Verneinung (dudar que, no creer que)** — _No creo que tenga razón._ (Ich glaube nicht, dass er recht hat.)
- **Wunschpartikel ojalá** — _Ojalá haga buen tiempo mañana._ (Hoffentlich ist morgen gutes Wetter.)

### Vollständig unregelmäßige Verben

**Verben mit eigenem Subjuntiv-Stamm**
|  | ser | ir | haber | saber | estar |
|---|---|---|---|---|---|
| yo | sea | vaya | haya | sepa | esté |
| tú | seas | vayas | hayas | sepas | estés |
| él, ella, usted | sea | vaya | haya | sepa | esté |
| nosotros, nosotras | seamos | vayamos | hayamos | sepamos | estemos |
| vosotros, vosotras | seáis | vayáis | hayáis | sepáis | estéis |
| ellos, ellas, ustedes | sean | vayan | hayan | sepan | estén |

> ⚠️ Deutsche Muttersprachler setzen nach 'dass' automatisch den Indikativ, weil das Deutsche hier keinen Subjuntivo verlangt. Merke: Nach 'querer que', 'espero que', 'es necesario que' usw. steht immer der Subjuntivo. Falsch: 'Quiero que vienes.' Richtig: 'Quiero que vengas.'

## `imperfecto-subjuntivo` — Imperfecto de Subjuntivo  (B2)
*hablara / hablase — Subjuntivo der Vergangenheit* · Konzept: `subjuntivo-imperfecto`

Der Imperfecto de Subjuntivo ist der Subjuntivo der Vergangenheit. Er steht in Nebensätzen, wenn der Hauptsatz in einer Vergangenheitszeit oder im Konditional steht, und ist zentral für irreale Bedingungssätze (si-Sätze) und höfliche Wünsche. Es gibt zwei gleichwertige Endungen: -ra und -se.

### Bildung

Man geht von der 3. Person Plural des Indefinido aus (ellos hablaron, comieron, vivieron), streicht die Endung -ron und hängt die Subjuntiv-Endungen an. So bleiben alle unregelmäßigen Stämme des Indefinido erhalten.

**Endungen -ra (Beispiele: hablar, comer, vivir)**
|  | hablar | comer | vivir |
|---|---|---|---|
| yo | hablara | comiera | viviera |
| tú | hablaras | comieras | vivieras |
| él, ella, usted | hablara | comiera | viviera |
| nosotros, nosotras | habláramos | comiéramos | viviéramos |
| vosotros, vosotras | hablarais | comierais | vivierais |
| ellos, ellas, ustedes | hablaran | comieran | vivieran |

**Endungen -se (gleichwertige Variante)**
|  | hablar | comer | vivir |
|---|---|---|---|
| yo | hablase | comiese | viviese |
| tú | hablases | comieses | vivieses |
| él, ella, usted | hablase | comiese | viviese |
| nosotros, nosotras | hablásemos | comiésemos | viviésemos |
| vosotros, vosotras | hablaseis | comieseis | vivieseis |
| ellos, ellas, ustedes | hablasen | comiesen | viviesen |

### Verwendung

- **Irreale Bedingung (si + Imperfecto de Subjuntivo)** — _Si tuviera más tiempo, viajaría por toda España._ (Wenn ich mehr Zeit hätte, würde ich durch ganz Spanien reisen.)
- **Subjuntiv-Auslöser in der Vergangenheit** — _Mi jefe me pidió que llegara antes de las nueve._ (Mein Chef bat mich, vor neun Uhr zu kommen.)
- **Höflicher Wunsch mit querer** — _Quisiera reservar una mesa para dos._ (Ich hätte gern einen Tisch für zwei reserviert.)
- **Nach como si (als ob)** — _Habla como si lo supiera todo._ (Er redet, als ob er alles wüsste.)
- **Nachzeitigkeit des Konditionals** — _Me gustaría que vinierais a la fiesta._ (Ich würde mich freuen, wenn ihr zur Party kämt.)

### Unregelmäßige Stämme (aus dem Indefinido)

**Da der Stamm aus der 3. Person Plural Indefinido kommt, bleiben die Unregelmäßigkeiten erhalten**
| Infinitiv | 3. Pl. Indefinido | Imperfecto de Subjuntivo (yo) |
|---|---|---|
| ser / ir | fueron | fuera / fuese |
| tener | tuvieron | tuviera / tuviese |
| hacer | hicieron | hiciera / hiciese |
| poder | pudieron | pudiera / pudiese |
| poner | pusieron | pusiera / pusiese |
| decir | dijeron | dijera / dijese |
| venir | vinieron | viniera / viniese |
| dar | dieron | diera / diese |
| pedir | pidieron | pidiera / pidiese |

> ⚠️ Nach si für eine irreale Bedingung steht nie das Konditional, sondern der Imperfecto de Subjuntivo. Falsch ist ‚Si tendría tiempo‘ — richtig ist ‚Si tuviera tiempo, iría‘. Das Konditional (iría) steht nur im Hauptsatz, der Subjuntivo im si-Satz.

## `oraciones-condicionales` — Oraciones Condicionales  (B2)
*si-Sätze: real und irreal* · Konzept: `condicional-irreal`

Die oraciones condicionales mit "si" drücken Bedingungen und ihre Folgen aus. Man unterscheidet reale Bedingungen (gut möglich), unwahrscheinliche oder unmögliche Bedingungen in der Gegenwart und Bedingungen der Vergangenheit, die nicht mehr eintreten können. Der gewählte Modus im si-Satz bestimmt die Bedeutung.

### Die drei Grundtypen

**Struktur der si-Sätze**
| Typ | si-Satz (Bedingung) | Hauptsatz (Folge) |
|---|---|---|
| Real | si + Presente de Indicativo | Presente / Futuro / Imperativo |
| Irreal Gegenwart | si + Imperfecto de Subjuntivo | Condicional Simple |
| Irreal Vergangenheit | si + Pluscuamperfecto de Subjuntivo | Condicional Compuesto |

### Beispielsätze der drei Typen

**Vollständige Sätze**
| Typ | Beispiel |
|---|---|
| Real | Si tienes tiempo, vamos al cine. |
| Irreal Gegenwart | Si tuviera tiempo, iría al cine. |
| Irreal Vergangenheit | Si hubiera tenido tiempo, habría ido al cine. |

### Verwendung

- **Reale, gut mögliche Bedingung** — _Si llueve mañana, nos quedamos en casa._ (Wenn es morgen regnet, bleiben wir zu Hause.)
- **Bedingung mit Aufforderung** — _Si termináis pronto, llamadme._ (Wenn ihr bald fertig seid, ruft mich an.)
- **Unwahrscheinliche Bedingung in der Gegenwart** — _Si fuéramos ricos, viviríamos junto al mar._ (Wenn wir reich wären, würden wir am Meer wohnen.)
- **Nicht mehr erfüllbare Bedingung in der Vergangenheit** — _Si hubieras estudiado más, habrías aprobado el examen._ (Wenn du mehr gelernt hättest, hättest du die Prüfung bestanden.)
- **Allgemeingültige Regel oder Gewohnheit** — _Si caliento agua a cien grados, hierve._ (Wenn ich Wasser auf hundert Grad erhitze, kocht es.)

### Mischformen

**Vergangene Bedingung mit gegenwärtiger Folge**
| si-Satz | Hauptsatz | Beispiel |
|---|---|---|
| Pluscuamperfecto de Subjuntivo | Condicional Simple | Si hubiera ahorrado más, ahora sería rico. |

> ⚠️ Nach "si" steht im irrealen Bedingungssatz NIE der Condicional und auch nicht das Presente de Subjuntivo. Falsch: "Si tendría tiempo" oder "Si tenga tiempo". Richtig ist der Imperfecto de Subjuntivo: "Si tuviera tiempo, iría". Der Condicional gehört nur in den Hauptsatz.

## `perifrasis-verbales` — Perífrasis Verbales  (B2)
*volver a, seguir + gerundio …* · Konzept: `perifrasis-verbales`

Als perífrasis verbales bezeichnet man feste Verbindungen aus einem konjugierten Hilfsverb und einer Verbform im Infinitiv, Gerundium oder Partizip. Sie drücken Nuancen aus, für die es im Deutschen oft nur Umschreibungen gibt: Wiederholung, Andauern, Beginn oder Ende einer Handlung.

### Die drei Grundtypen

**Struktur nach Verbform**
|  | Struktur | Bedeutung |
|---|---|---|
| Infinitiv | volver a + Infinitiv | etwas wieder tun |
| Infinitiv | ir a + Infinitiv | etwas gleich/bald tun |
| Infinitiv | acabar de + Infinitiv | gerade getan haben |
| Gerundium | seguir + Gerundium | weiterhin tun |
| Gerundium | llevar + Gerundium | seit einer Dauer tun |
| Gerundium | estar + Gerundium | gerade dabei sein |
| Partizip | llevar + Partizip | bereits erledigt haben |

### seguir + Gerundium konjugiert

**Beispiel: seguir trabajando (weiterarbeiten)**
|  | seguir | + Gerundium |
|---|---|---|
| yo | sigo | trabajando |
| tú | sigues | trabajando |
| él, ella, usted | sigue | trabajando |
| nosotros, nosotras | seguimos | trabajando |
| vosotros, vosotras | seguís | trabajando |
| ellos, ellas, ustedes | siguen | trabajando |

### Verwendung

- **Wiederholung einer Handlung** — _Ha vuelto a llover esta tarde._ (Es hat heute Nachmittag wieder geregnet.)
- **Andauern eines Zustands** — _Sigo viviendo en el mismo piso._ (Ich wohne weiterhin in derselben Wohnung.)
- **Dauer bis zum Sprechzeitpunkt** — _Llevo tres años estudiando español._ (Ich lerne seit drei Jahren Spanisch.)
- **Etwas gerade Abgeschlossenes** — _Acabo de salir del trabajo._ (Ich habe gerade Feierabend gemacht.)
- **Naher Zukunftsbezug** — _Vamos a cenar en casa de mis padres._ (Wir werden bei meinen Eltern zu Abend essen.)

### Besonderheiten der Konstruktion

**Stellung der Pronomen**
|  | Beispiel | Deutsch |
|---|---|---|
| vor dem Hilfsverb | Lo sigo estudiando. | Ich lerne es weiterhin. |
| angehängt am Gerundium | Sigo estudiándolo. | Ich lerne es weiterhin. |
| vor dem Hilfsverb (Infinitiv) | Lo voy a llamar. | Ich werde ihn anrufen. |
| angehängt am Infinitiv | Voy a llamarlo. | Ich werde ihn anrufen. |

> ⚠️ Deutsche verwechseln oft 'volver a + Infinitiv' (wieder tun) mit 'volver' (zurückkehren). 'Vuelvo a leerlo' heißt 'Ich lese es erneut', nicht 'Ich kehre zurück, um es zu lesen'. Und nach 'volver a' steht immer der Infinitiv, nie das Gerundium: nicht *vuelvo a leyendo*.

## `marcadores-temporales` — Marcadores Temporales  (B2)
*desde, hace, durante — Zeitangaben* · Konzept: `desde-hace-durante`

Die marcadores temporales desde, hace und durante geben an, seit wann, vor wie langer Zeit oder während welches Zeitraums etwas geschieht. Sie sind zentral, um Dauer, Ausgangspunkt und Zeitspanne einer Handlung präzise auszudrücken, und werden oft verwechselt.

### Grundformen und ihre Bedeutung

**Die drei Marker im Überblick**
| Marker | Bedeutung | Bezug |
|---|---|---|
| desde | seit (Ausgangspunkt) | konkreter Zeitpunkt in der Vergangenheit |
| desde hace | seit (Dauer) | verstrichene Zeitspanne bis heute |
| hace | vor / seit (Abstand) | Zeit, die seit einem Ereignis vergangen ist |
| durante | während / (für die Dauer von) | abgeschlossener oder gesamter Zeitraum |

### Satzstellung

**Konstruktion mit Beispielangabe**
|  | Struktur | Beispielangabe |
|---|---|---|
| desde | desde + Zeitpunkt | desde 2010, desde el lunes |
| desde hace | desde hace + Zeitspanne | desde hace tres años |
| hace ... que | hace + Zeitspanne + que | hace tres años que |
| hace | hace + Zeitspanne (Abstand) | hace dos días |
| durante | durante + Zeitraum | durante el verano |

### Verwendung

- **Ausgangspunkt mit desde** — _Vivo en Valencia desde 2015._ (Ich wohne seit 2015 in Valencia.)
- **Andauernde Handlung: desde hace** — _Estudio alemán desde hace dos años._ (Ich lerne seit zwei Jahren Deutsch.)
- **Gleiche Aussage mit hace ... que** — _Hace dos años que estudio alemán._ (Seit zwei Jahren lerne ich Deutsch.)
- **Zeitlicher Abstand zu einem Ereignis** — _Terminé la carrera hace cinco años._ (Ich habe mein Studium vor fünf Jahren abgeschlossen.)
- **Zeitraum mit durante** — _Durante las vacaciones no trabajamos._ (Während der Ferien arbeiten wir nicht.)

### desde vs. desde hace

**Zeitpunkt oder Zeitspanne**
|  | desde (Zeitpunkt) | desde hace (Dauer) |
|---|---|---|
| Beispiel | desde el martes | desde hace tres días |
| Frage | ¿Desde cuándo? | ¿Desde cuándo? / ¿Cuánto tiempo hace? |
| Antwortfokus | ab wann es begann | wie lange es schon dauert |

> ⚠️ Deutsche übersetzen 'seit' oft pauschal mit desde: 'Vivo aquí desde tres años' ist falsch. Bei einer Zeitspanne (drei Jahre) muss desde hace stehen: 'Vivo aquí desde hace tres años'. Desde allein nur vor einem konkreten Zeitpunkt (desde 2020, desde marzo). Und hace bezeichnet den Abstand ('vor drei Jahren'), nicht die Dauer bis heute.

## `voz-pasiva-refleja` — Voz Pasiva y Pasiva Refleja  (B2)
*ser + participio und das Reflexivpassiv* · Konzept: `voz-pasiva`

Das Passiv rückt die Handlung oder das betroffene Objekt in den Vordergrund, während der Handelnde unwichtig oder unbekannt bleibt. Im Spanischen gibt es zwei Wege: die Vorgangspassiv-Konstruktion mit ser + Partizip (voz pasiva) und die weit häufigere pasiva refleja mit se, die im Alltag klar bevorzugt wird.

### Voz pasiva: ser + Partizip

Das Partizip richtet sich in Geschlecht und Zahl nach dem Subjekt. Der Handelnde wird, wenn genannt, mit der Präposition por eingeleitet.

**ser + Partizip (Beispiel: publicar)**
|  | ser | Partizip |
|---|---|---|
| Singular mask. | es / fue | publicado |
| Singular fem. | es / fue | publicada |
| Plural mask. | son / fueron | publicados |
| Plural fem. | son / fueron | publicadas |

### Pasiva refleja: se + Verb

Das Verb steht in der 3. Person und richtet sich in der Zahl nach dem grammatischen Subjekt (der Sache). Kein Handelnder wird genannt.

**Pasiva refleja**
|  | Singular | Plural |
|---|---|---|
| Präsens | se vende | se venden |
| Indefinido | se vendió | se vendieron |
| Perfekt | se ha vendido | se han vendido |
| Futur | se venderá | se venderán |

### Verwendung

- **Formeller/schriftlicher Vorgang mit ser** — _La ley fue aprobada por el Parlamento en 2020._ (Das Gesetz wurde 2020 vom Parlament verabschiedet.)
- **Handelnder unbekannt oder unwichtig (pasiva refleja)** — _Aquí se hablan varios idiomas._ (Hier werden mehrere Sprachen gesprochen.)
- **Schilder und Anzeigen** — _Se vende piso. Se buscan camareros._ (Wohnung zu verkaufen. Kellner gesucht.)
- **Anleitungen und Rezepte** — _Primero se cortan las verduras y se fríen en aceite._ (Zuerst schneidet man das Gemüse und brät es in Öl.)
- **Allgemeine Aussagen ohne Subjekt** — _En España se cena muy tarde._ (In Spanien isst man sehr spät zu Abend.)

### Unregelmäßige Partizipien im Passiv

**Häufige unregelmäßige Partizipien**
|  | Partizip | Beispiel |
|---|---|---|
| escribir | escrito | La carta fue escrita ayer. |
| hacer | hecho | El trabajo está hecho. |
| abrir | abierto | La tienda fue abierta a las ocho. |
| romper | roto | Los vasos fueron rotos. |
| resolver | resuelto | El caso fue resuelto. |

> ⚠️ Deutschsprachige übertragen das deutsche 'werden'-Passiv oft direkt mit ser + Partizip. Im Spanien-Spanisch klingt das im Alltag steif und schriftsprachlich. Statt 'La casa fue construida en 1990' sagt man normalerweise 'La casa se construyó en 1990'. Denk außerdem an die Zahl-Kongruenz bei der pasiva refleja: 'Se venden pisos' (Plural!), nicht 'Se vende pisos'.

## `estilo-indirecto` — Estilo Indirecto  (B2)
*dijo que … — die indirekte Rede* · Konzept: `estilo-indirecto`

Der estilo indirecto gibt wieder, was jemand gesagt, gefragt oder gefordert hat, ohne die Worte wörtlich zu zitieren. Statt «Voy a casa» sagst du «Dijo que iba a casa». Wenn das einleitende Verb in der Vergangenheit steht, verschieben sich Zeiten, Pronomen und Zeitangaben.

### Zeitenverschiebung nach Vergangenheit

**Wechsel der Verbzeit, wenn das einleitende Verb (dijo, preguntó …) in der Vergangenheit steht**
| Direkte Rede | Indirekte Rede |
|---|---|
| Presente (trabajo) | Imperfecto (trabajaba) |
| Pretérito Perfecto (he trabajado) | Pluscuamperfecto (había trabajado) |
| Indefinido (trabajé) | Pluscuamperfecto (había trabajado) |
| Imperfecto (trabajaba) | Imperfecto (trabajaba) |
| Futuro (trabajaré) | Condicional (trabajaría) |
| Imperativo (trabaja) | Imperfecto de Subjuntivo (trabajara) |
| Presente de Subjuntivo (trabaje) | Imperfecto de Subjuntivo (trabajara) |

### Verschiebung von Zeit- und Ortsangaben

**Wechsel der Deiktika bei zeitlicher Distanz**
| Direkte Rede | Indirekte Rede |
|---|---|
| hoy | aquel día |
| ayer | el día anterior |
| mañana | el día siguiente |
| ahora | entonces |
| aquí | allí |
| este/esta | ese/esa |

### Verwendung

- **Aussage wiedergeben** — _Dijo que estaba cansado y que se iría pronto._ (Er sagte, dass er müde sei und bald gehen werde.)
- **Ja/Nein-Frage wiedergeben (si)** — _Me preguntó si había terminado el informe._ (Sie fragte mich, ob ich den Bericht fertig hätte.)
- **Ergänzungsfrage wiedergeben (mit Fragewort)** — _Nos preguntó dónde vivíamos._ (Er fragte uns, wo wir wohnten.)
- **Aufforderung oder Bitte wiedergeben** — _El médico me dijo que descansara unos días._ (Der Arzt sagte mir, ich solle mich ein paar Tage ausruhen.)
- **Wiedergabe im Präsens (keine Verschiebung)** — _Dice que viene esta tarde._ (Sie sagt, dass sie heute Nachmittag kommt.)

### Einleitende Verben und Anschluss

**Typische Verben und ihr Anschluss**
|  | Beispiel |
|---|---|
| Aussage (que) | Comentó que vosotros teníais razón. |
| Ja/Nein-Frage (si) | Preguntó si veníais con nosotros. |
| W-Frage (Fragewort) | Quiso saber cuándo llegabais. |
| Aufforderung (que + Subjuntivo) | Os pidió que llegarais a tiempo. |

> ⚠️ Deutschsprachige übernehmen bei der W-Frage oft den Akzent nicht: Auch im estilo indirecto behält das Fragewort seinen Akzent (Me preguntó qué quería, dónde vivía, cuándo llegaba) — obwohl kein Fragezeichen mehr steht.
