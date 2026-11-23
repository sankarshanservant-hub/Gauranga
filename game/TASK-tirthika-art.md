# Задание на графику: сцена «Брахман-паломник» (ЧБ Ади 5)

Что нужно от пользователя (через ChatGPT) и что — решениями. Готовые картинки класть в папку Диска
`Gauranga-game/ref/` (имена файлов — как указано), Claude заберёт их сам.

## Общие правила для всех картинок GPT
- **Один чат на одного персонажа:** сначала портрет, потом в том же чате — «лист персонажа» (тот же человек).
- Формат: портрет — вертикальный 3:4; лист персонажа — горизонтальный, светло-серый фон.
- Всегда добавлять в конец промпта: *Historically accurate Bengal, around 1490 AD. Simple handwoven cotton, no modern
  objects, no text, no watermark. Dignified, devotional, gentle atmosphere.*
- Женщины: *sari draped modestly over both shoulders and the upper body, the end of the sari over the head.*
- Замужние женщины (Шачи, соседка): **красная точка синдура на лбу + синдур в проборе, без полос тилаки** — так по
  житиям (Лочан, Ади ч. 14, 84, 109: «синдур на лоб»; Мадхья ч. 15, 68+16–17: «точка синдура», вокруг — точки сандала).
  Полосы урдхва-пундры у женщин — поздняя практика; если учитель решит иначе — поправим.
- Если GPT рисует «сказочно» или по-европейски — ответить: *more realistic, Bengali faces and skin tones, painted like a classical
  oil portrait, less cartoonish*.
- Если что-то выглядит не по-вайшнавски (мирская трактовка, украшения не той эпохи) — лучше перегенерировать, чем исправлять.

## 1. Портреты для диалогов (главное — в них лица)
Шаблон (подставить описание):
> Painted RPG character portrait in the style of Baldur's Gate II portraits, oil painting, bust, three-quarter view,
> soft warm light, dark neutral background. [ОПИСАНИЕ]. Historically accurate Bengal, around 1490 AD…

| Файл | Описание для [ОПИСАНИЕ] |
|---|---|
| `portrait_mishra.png` | Jagannatha Mishra, a gentle Bengali brahmin householder about 55 years old, kind tired eyes, grey shikha (tuft of hair), clean-shaven, Vaishnava tilak (two vertical white lines) on the forehead, white sacred thread across the bare chest, white cotton dhoti and a white shawl (uttariya) over one shoulder, tulasi bead necklace |
| `portrait_shachi.png` | Shachi Devi, a noble Bengali brahmin mother about 40, serene loving face, white cotton sari with a thin red border worn over the head, a small round red sindur dot (bindu) on the forehead and red sindur in the hair parting, NO vertical tilak lines, white conch-shell and red bangles, tulasi necklace |
| `portrait_nimai.png` | Nimai, a radiant little boy about 4 years old with golden skin, large lotus-shaped eyes, curly black hair, a mischievous smile, a little dust on his cheeks, a simple tulasi necklace; divine but childlike, never adult features |
| `portrait_brahmana.png` | a wandering Vaishnava brahmin pilgrim about 60, thin and ascetic, long grey beard and shikha, Vaishnava tilak, eyes half-closed in remembrance, a small Bala-Gopala deity and a Shalagram stone in a cloth pouch hanging at his chest, white worn dhoti and shawl |
| `portrait_vishvarupa.png` | Vishvarupa, a radiant Bengali brahmin youth about 14, effulgent calm face, sacred thread, shikha, Vaishnava tilak, white dhoti and shawl, scholarly and saintly |
| `portrait_relative.png` | a middle-aged Bengali brahmin relative, ochre shawl, sacred thread, tilak, friendly worried face |
| `portrait_neighbor.png` | a cheerful middle-aged Bengali village woman, indigo cotton sari with a mustard border over the head, red sindur dot on the forehead, conch-shell bangles |
| `portrait_gandharva_a/b/c.png` | three variants of the hero: a young celestial musician (gandharva), luminous bluish-gold skin, a vina over his shoulder, a delicate golden crown, flowing light celestial garments, wonder and humility in his eyes — (a) more Indian-miniature, (b) more painterly-realistic, (c) female variant: a young apsara musician |
| `portrait_chitrasena.png` | Chitrasena, king of the gandharvas, a noble mature celestial musician with a vina, golden crown, luminous skin, wise smile |
| `portrait_nidra.png` | Nidra Devi, goddess of sleep, serene dark-blue skin, deep blue sari with stars, half-closed eyes, a soft veil of night around her |

### Рассказчик (вместо буквы «Ш» в окне «Шри Чайтанья-бхагавата»)
| Файл | Промпт |
|---|---|
| `narr_cb_author.png` | Painted RPG character portrait in the style of Baldur's Gate II portraits, oil painting, bust, three-quarter view, soft warm lamplight, dark neutral background. Srila Vrindavana dasa Thakura, a saintly young Bengali Vaishnava poet about 35, serene absorbed face, shaved head with shikha, Vaishnava tilak, tulasi bead necklace, simple white cotton cloth and shawl, writing with a stylus on long palm-leaf manuscript pages, a small oil lamp beside him. Historically accurate Bengal, 16th century. Dignified, devotional, gentle atmosphere. No text, no watermark. |
| `narr_cb_book.png` | Painted illustration in the style of Baldur's Gate II portraits, oil painting, dark warm background, soft lamplight. An old Bengali palm-leaf manuscript (puthi) between two carved wooden covers, partly unwrapped from a red cloth, a garland of tulasi leaves and a small clay lamp beside it. Devotional, reverent atmosphere. No readable text, no watermark. |

Для следующих глав — так же для других рассказчиков (`narr_cc_author` — Кришнадас Кавирадж Госвами, `narr_lochana_author`,
`narr_murari_author`).

## 2. Листы персонажей (по ним делаются 3D-модели и одежда)
В том же чате, после портрета:
> Now make a character turnaround sheet of the same person: full body, front view, side view and back view, neutral
> standing A-pose, arms slightly away from the body, plain light grey background, consistent proportions,
> realistic style, the same clothes.

Файлы: `sheet_mishra.png`, `sheet_shachi.png`, `sheet_nimai.png`, `sheet_brahmana.png`, `sheet_vishvarupa.png`,
`sheet_gandharva.png` (выбранный вариант).


### Листы для оставшихся (родственник, соседка, Читрасена, Нидра)
После общего промпта листа добавить уточнение (и: *Barefoot. Historically accurate Bengal, around 1490 AD, no modern objects, no text.*):
| Файл | Уточнение |
|---|---|
| `sheet_relative.png` | A middle-aged Bengali brahmin, ochre cotton shawl over one shoulder, white dhoti to the ankles, sacred thread, shikha, Vaishnava tilak, tulasi necklace. |
| `sheet_neighbor.png` | A middle-aged Bengali village woman, indigo cotton sari with a mustard border, draped modestly over both shoulders and over the head, no blouse sleeves visible, red sindur dot on the forehead and sindur in the hair parting, white conch-shell bangles. |
| `sheet_chitrasena.png` | Chitrasena, king of the gandharvas: tall noble celestial musician, golden crown, long dark wavy hair, white and gold silk garments with a shawl, gold ornaments, a vina held at his side (not covering the body), luminous skin. |
| `sheet_nidra.png` | Nidra Devi, goddess of sleep: serene dark-blue skin, deep blue sari with tiny silver stars draped over the head and both shoulders, half-closed eyes, a soft night-blue shawl; full figure clearly visible, no smoke or mist hiding the body. |

Для 3D: предметы держать сбоку, а не поперёк тела (иначе «прилипнут»); без дымки и тумана вокруг фигуры — свечение
добавляется в игре.

## 3. Ткани (бесшовные текстуры для одежды)
> Seamless tileable texture, flat top view, handwoven [ткань], no shadows, no folds, square.

`tex_white_cotton.png` (white handwoven cotton, slightly uneven threads), `tex_sari_red_border.png` (white cotton sari with a
thin red border along one edge), `tex_indigo_sari.png`, `tex_ochre_cotton.png`, `tex_celestial_silk.png`
(light celestial silk with golden shimmer).

## 4. Иллюстрации к карточкам быта (по желанию, очень украсят журнал)
> Small painted illustration for a museum codex card, watercolor and ink on old paper, isolated object, no text: [ПРЕДМЕТ].

20 предметов (файл `codex_<имя>.png`): tulasi altar (tulasi-mancha) with a clay lamp; rice-paste alpana floor
pattern; clay oil lamp (pradip); clay cooking pots (handi); brass and bell-metal vessels; a Bengali clay stove (chula);
firewood stack; thatched mud hut (chala) with a veranda; cow-dung cakes drying on a mud wall; rice-straw stack around a pole;
village pond with brick steps (ghat); white sari with red border drying on a line; banana plant; bunch of bananas and fruits;
coconut palm; bamboo grove; cowshed with a cow; hanging brass lamp; low wooden seat (pidi); woven bamboo fence.

## 5. Mixamo — дополнительно (по желанию)
Уже есть 28 анимаций, хватает. Если будет время: `Female Walk`, `Female Standing Pose` / `Happy Idle` (для Шачи и
соседки), `Sitting Idle` в варианте «на полу, скрестив ноги», `Praying` в позе сидя. Те же настройки: Without Skin,
30 fps, Keyframe Reduction — none; для ходьбы — In Place.

## 6. Решения (лучше — с учителем)
1. **Герой:** безымянный гандхарва / апсара Рамбха (ЧЧ Ади 13.105) / Тумбуру / ученик Нарады / иное. Имя.
2. **Лицо Господа:** показывать ли портрет Нимая крупно в диалоге (сейчас — да, детский) и как в будущем изображать
   взрослого Махапрабху.
3. **Слово ачарьи:** есть ли у Шрилы Б. Р. Шридхара Махараджа (или в лекциях миссии) слова об этой лиле — тогда
   прислать цитату/ссылку, она войдёт в карточку лилы.
4. **Звук:** записи киртана и раковины, улу-дхвани; можно ли использовать записи миссии.
5. **Название игры.**
