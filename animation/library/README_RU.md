# Библиотека по 2D-анимации для проекта «Нитьянанда»

Подборка для работы над ходьбой персонажа в дхоти: механика шага, ткань поверх идущих ног,
деформация плоского рисунка сеткой, перекладка (cut-out).

**Правило подборки.** В репозиторий скачано только то, что можно законно свободно хранить:
общественное достояние или открытая лицензия. Книги и статьи под охраной авторского права не
хранятся — для них даны выходные данные и ссылка на законный источник. Прочитанное изложено своими
словами в [`KONSPEKT_RU.md`](KONSPEKT_RU.md) вместе с выводами для нашей ходьбы.

## 1. Скачано: общественное достояние (`public_domain/`)

| Файл | Что это | Источник | Чем полезно |
|---|---|---|---|
| `Lutz_1920_Animated_Cartoons.pdf`, `…_gutenberg.txt` | E. G. Lutz, *Animated Cartoons: How They Are Made, Their Origin and Development* (Scribner, 1920) | archive.org `cu31924075701304`; Project Gutenberg #73455 | Классическое описание шага: перекат стопы, колено в переносе, положение прохода, подъём и опускание корпуса, руки в противофазе. Порядок рисования фаз ходьбы. |
| `Bridgman_1920_Constructive_Anatomy.pdf`, `.txt` | G. B. Bridgman, *Constructive Anatomy* (1920) | archive.org `cu31924014504371` | Строение таза, бедра, колена, стопы: что меняется в форме ноги при сгибе. |
| `Marey_1895_Movement.pdf`, `.txt` | É.-J. Marey, *Movement*, пер. E. Pritchard (1895) | archive.org `movement00mare` | Хронофотография ходьбы. Траектория головы (центра тяжести): высшая точка в середине опоры, низшая при смене ног. Длина и частота шага. Нога как двузвенный маятник. |
| `Muybridge_1887_Animal_Locomotion_catalogue_of_plates.pdf`, `.txt` | E. Muybridge, *Animal Locomotion*: проспект и каталог 781 таблицы (1887) | archive.org `cu31924024580353` | Обозначения одежды моделей, в том числе «P. C.» (повязка на бёдрах) и «T. D.» (прозрачная драпировка). Номера таблиц. |
| `Muybridge_1893_Descriptive_Zoopraxography.pdf`, `.txt` | E. Muybridge, *Descriptive Zoopraxography* (1893) | archive.org `descriptivezoopr00muyb` | Пояснения к фазам движения по фотографиям. |
| `muybridge_plates/*.jpg`, `plates.json` | 10 таблиц *Animal Locomotion* (1887), коллотипии | Wellcome Collection, Public Domain Mark | См. таблицу ниже. |

### Таблицы Мейбриджа (`public_domain/muybridge_plates/`)

| Файл | Таблица | Содержание | Зачем нам |
|---|---|---|---|
| `hvmzn53q.jpg` | 56 | женщина идёт в длинной прозрачной драпировке, сбоку / спереди / сзади | **главная**: как ткань ложится на выносимое колено и складывается позади ноги |
| `q7fzdkdw.jpg` | — | то же, лёгкое платье | ткань поверх шага |
| `mpfvpaa8.jpg` | — | ходьба в прозрачном платье | ткань поверх шага |
| `dzds4pkd.jpg` | 232 | отрез ткани закреплён на бёдрах (наклон, поднимает ткань) | поведение ткани, закреплённой на поясе, — ближе всего к дхоти |
| `zqx8348p.jpg`, `bzddsb9c.jpg` | — | мужчина в набедренной повязке идёт | мужская ходьба с тканью на бёдрах |
| `arjhfnhj.jpg`, `bevkgxdz.jpg`, `wrt55hpp.jpg`, `bgd7pfcz.jpg` | — | мужчина идёт, профиль | скелет шага: фазы, сгиб колена, перекат стопы |

Это научные фотографии 1887 года; на части таблиц модели обнажены.

## 2. Прочитано, не хранится (охраняемые тексты; ссылки на законные копии)

| Источник | Где | Что взято в конспект |
|---|---|---|
| J. Lasseter, *Principles of Traditional Animation Applied to 3D Computer Animation*, SIGGRAPH 1987 | [SIGGRAPH Education](https://education.siggraph.org/static/HyperGraph/animation/character_animation/principles/prin_trad_anim.htm); [история SIGGRAPH](https://history.siggraph.org/?p=116057) | 12 принципов, в первую очередь доводка и захлёст движения, второстепенное действие, дуги, плавный разгон и торможение |
| T. Igarashi, T. Moscovich, J. Hughes, *As-Rigid-As-Possible Shape Manipulation*, SIGGRAPH 2005 | [страница авторов](https://www-ui.is.s.u-tokyo.ac.jp/~takeo/research/rigid); [PDF авторов](https://www-ui.is.s.u-tokyo.ac.jp/~takeo/papers/rigid.pdf); реализация: [JGT 2009](https://www-ui.is.s.u-tokyo.ac.jp/~takeo/papers/takeo_jgt09_arapFlattening.pdf) | деформация плоского рисунка с наименьшим искажением треугольников; жёсткость по областям; порядок слоёв при перекрытии |
| A. Jacobson, I. Baran, J. Popović, O. Sorkine, *Bounded Biharmonic Weights for Real-Time Deformation*, SIGGRAPH 2011 | [PDF](https://homes.cs.washington.edu/~jovan/papers/jacobson-2011-bbw.pdf); [страница проекта](https://www.alecjacobson.com/weblog/1784.html) | автоматические гладкие локальные веса для костей под тканью |
| Disney, *Class on Action Analysis*, Lecture V «Walks and Runs» (Don Graham, 22.03.1937) | [DIX Project](https://www.dix-project.net/document/disney-class-on-action-analysis_1937-03-22_lecture-v-walks-and-runs) | только описание: текст лекции дан сканами страниц, не прочитан |
| Документация Godot: *Cutout animation*, Skeleton2D, Polygon2D | [docs.godotengine.org](https://docs.godotengine.org/en/stable/tutorials/animation/cutout_animation.html) | RemoteTransform2D и смена порядка слоёв во время анимации; IK в Godot — только в редакторе |
| Live2D Cubism: деформаторы, параметры и ключевые формы | [руководство](https://docs.live2d.com/en/cubism-editor-manual/top); [движение тела](https://docs.live2d.com/en/cubism-editor-tutorials/deformer/) | рисованные ключевые формы по параметру и их смешивание — путь к нарисованной позе дхоти для фазы переноса |
| Spine: веса и привязка сетки к костям | [Weights view](https://fr.esotericsoftware.com/spine-weights.md) | практика весов в 2D-сетках |
| Нормативные данные ходьбы (ZHAW, открытые данные) | [ZHAW](https://www.zhaw.ch/en/health/health-research-and-development/research-news/event-news/open-data-on-normal-human-gait) | для сверки кривых сгиба колена, если понадобится; не скачивалось |

## 3. Стоит купить или взять в библиотеке (охраняются; не скачивал)

**Ходьба и тайминг — основа:**
- (законспектирована, см. раздел 4) Richard Williams, *The Animator's Survival Kit* (Faber & Faber, 2001; расширенное изд. 2009). Самый подробный разбор ходьбы: контакт, опускание, проход, подъём, вес, характер походки. **Первая книга, если брать одну.**
- Harold Whitaker, John Halas, *Timing for Animation* (Focal Press, 1981; 2-е изд. 2009, ред. T. Sito). Тайминг шага, ткань и волосы, захлёст движения.
- Frank Thomas, Ollie Johnston, *The Illusion of Life: Disney Animation* (1981). Принципы анимации и их происхождение.
- Preston Blair, *Cartoon Animation* (Walter Foster, 1994; нов. изд. 2020). Компактные схемы шагов и походок.
- Eric Goldberg, *Character Animation Crash Course!* (Silman-James, 2008).
- Chris Webster, *Animation: The Mechanics of Motion* (Focal Press, 2005).
- Walt Stanchfield, *Drawn to Life: 20 Golden Years of Disney Master Classes*, т. 1–2 (Focal Press, 2009). Жест и читаемость позы.

**Ткань и одежда:**
- (законспектирована, см. раздел 4) Burne Hogarth, *Dynamic Wrinkles and Drapery* (Watson-Guptill, 1995). Типы складок, натяжение ткани на движущемся колене.

**Перекладка (cut-out) — ближе всего к нашей технике:**
- (законспектирована, см. раздел 4) Юрий Норштейн, «Снег на траве» (лекции; изд. 2005/2008). Перекладка изнутри: как один рисунок делится на подвижные части.
- Фёдор Хитрук, «Профессия — аниматор», т. 1–2 (Гаятри, 2007).
- Иван Иванов-Вано, «Рисованный фильм» (Госкиноиздат, 1950).
- Kit Laybourne, *The Animation Book* (1979; новое изд. 1998). Глава о перекладке.

**Биомеханика ходьбы:**
- Jacquelyn Perry, Judith Burnfield, *Gait Analysis: Normal and Pathological Function* (SLACK, 2-е изд. 2010).
- W. Braune, O. Fischer, *The Human Gait* (англ. пер. Springer, 1987; ориг. *Der Gang des Menschen*, 1895–1904).
- E. Muybridge, *The Human Figure in Motion* (Dover, 1955) — подборка 196 таблиц; сами таблицы 1887 г. в общественном достоянии.

## 4. Книги, присланные пользователем: конспекты (`konspekt/`)

Книги под авторским правом. Сами PDF в репозиторий не входят (репозиторий публичный), здесь только конспекты
своими словами с привязкой к нашей перекладке в Godot и к сценам жизни Шри Чайтаньи. В начале каждого — сводка.

| Конспект | Книга | Главное для нас |
|---|---|---|
| [`Williams_Survival_Kit_RU.md`](konspekt/Williams_Survival_Kit_RU.md) | Richard Williams, *The Animator's Survival Kit* (Faber & Faber, 2001) | тайминг и интервалы, ходьба и бег по кадрам, танец (подскок), захлёст и последовательный «излом» суставов, вес, антиципация, акценты, диалог, игра, животные, порядок работы |
| [`Hogarth_Wrinkles_Drapery_RU.md`](konspekt/Hogarth_Wrinkles_Drapery_RU.md) | Burne Hogarth, *Dynamic Wrinkles and Drapery* (Watson-Guptill, 1995) | девять систем складок; дхоти, чадар, тюрбан в движении; что заказать художнику (46 форм) |
| [`Norshtein_Sneg_na_trave_RU.md`](konspekt/Norshtein_Sneg_na_trave_RU.md) | Ю. Б. Норштейн, «Снег на траве. Фрагменты книги» (ВГИК, 2005) | перекладка изнутри: устройство персонажа, ярусы и глубина, свет и фактура, пауза и ритм, звук, монтаж, толпа, создание образа |

Отсылки к лилам в разделах «→ Для нас» — рабочие идеи исполнителей; перед использованием в сценарии сверять с
житиями (`lila-db/`).

## Журнал поиска

- Preston Blair, *Animation* (1947/48): свободной законной копии не найдено; статус охраны не ясен — не скачивалось.
- Braune & Fischer: свободной копии не найдено.
- Marey, *Movement*: страница Biodiversity Heritage Library не открылась из среды; взята копия archive.org.
- Национальная галерея искусства США (открытые изображения таблиц Мейбриджа): сайт закрыт для автоматического доступа (403); таблицы взяты в Wellcome Collection.
- Лекция Disney о ходьбе (1937): на DIX Project только сканы страниц, распознанного текста нет.
