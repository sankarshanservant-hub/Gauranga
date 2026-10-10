# Промпты для иллюстраций лил

Общие требования ко всем картинкам ленты:
- Стиль — старинная бенгальская миниатюра / ручная роспись XIX в. (как на макете), мягкие приглушённые краски,
  тонкий тёмно-коричневый контур, лёгкая сепия.
- **Без собственного фона**: виньетка на чистом белом (или прозрачном) фоне, края мягко растворяются. На сайте белое
  исчезает на бумаге свитка (режим «умножение»), поэтому никакой рамки, неба до краёв, тёмного или цветного фона.
- Вертикальный формат 4:5 (например, 1024×1280 или больше). Главные фигуры — в центре, вокруг воздух.
- Богословская точность (гаудия-вайшнавская): Господь — не обычный младенец; золотое сияние, лотосные очи;
  никаких мирских, сентиментальных или «театральных» трактовок.

## Явление Шри Гауранги (`ev-gaura-appearance`)

По писаниям: Мурари Гупта 1.5.16–22, Карнапура (махакавья 2.38–44; «Чайтанья-чандродая» 1.20), Лочан Дас
(«Джанма-лила» 47–80), «Гаура-кришнодая» 2.9–18, пады Васу Гхоша и Нарахари. Полночь полнолуния месяца пхалгуна;
лунное затмение (Раху поглощает луну), повсюду поют «Хари! Хари!»; дитя золотистое, с лотосными очами, лицом как
полная луна, рассеивает тьму своим сиянием; боги ликуют и сыплют цветы; Шачи зовёт Джаганнатху Мишру взглянуть на сына.

**Промпт (EN):**

> Antique Bengali miniature painting, 19th-century hand-painted devotional illustration, soft muted earth pigments,
> fine dark-brown ink outlines, gentle sepia patina, isolated vignette on a plain pure white background with softly
> fading edges, no frame, no border, vertical 4:5 composition.
> The divine appearance of Sri Chaitanya Mahaprabhu (Gauranga) on the full-moon night of Phalguna, 1486, in Navadvipa.
> In the centre, Mother Shachi, a young Bengali brahmin woman in a white sari with a red border, sits on a simple mat
> inside a thatched birth-room doorway, tenderly holding the newborn Gauranga. The infant is radiant, molten-golden in
> complexion, with lotus-petal eyes and a face like the full moon; a soft golden effulgence glows around Him and
> dispels the darkness. Beside her stands Jagannatha Mishra, a learned elderly brahmin with a white dhoti, sacred
> thread, shikha and Vaishnava tilaka, looking at his son with joyful wonder, hands folded.
> Above them, in the night sky, a full moon partly covered by the lunar eclipse; tiny celestial devas peep from small
> clouds and shower flowers. In the background, faint and light: a neem tree, a few village women blowing conch shells,
> and people bathing in the Ganges chanting the holy name. Calm, sacred, joyful mood; reverent, not sentimental.

**Negative prompt / чего избегать:** dark background, coloured background, full-bleed sky, frame, border, text,
watermark, signature, modern style, photorealism, 3D render, Western cherub angels, halo as a flat disc, blue-skinned
infant, harsh saturated colours, cluttered composition.

**Тот же промпт по-русски (для понимания):** старинная бенгальская миниатюра XIX в., приглушённые краски, тонкий
коричневый контур, сепия; виньетка на чисто белом фоне без рамки, края растворяются; вертикально 4:5. Ночь полнолуния
пхалгуны, Навадвипа. В центре Шачи в белом сари с красной каймой держит новорождённого Гаурангу — золотого, сияющего,
с лотосными очами и лицом как полная луна; сияние рассеивает тьму. Рядом Джаганнатха Мишра — пожилой брахман
(дхоти, священный шнур, шикха, тилака), сложив ладони, с радостным изумлением смотрит на сына. Вверху — луна в
затмении, полубоги в облаках сыплют цветы. На заднем плане, легко и бледно, — дерево ним, женщины трубят в раковины,
люди омываются в Ганге и поют святое имя. Настроение — священная радость, благоговение.

Готовую картинку назвать `ev-gaura-appearance.png` — подключу в `app.js` (`IMAGES`).
