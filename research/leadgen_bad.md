# Трафик и лидогенерация для БАД, РФ и США, на 12.11.2026

**Оговорка о проверке.** Всё ниже собрано из выдачи WebSearch. Открыть первоисточники через WebFetch не удалось: consultant.ru, pravo.ru, yandex.ru, ads.vk.ru, rg.ru, expert.ru и др. недоступны из сетевого окружения сессии. Тексты законов и правил площадок я не читал; номера и даты взяты из пересказов.

Метки: [З] закон/официальный источник в пересказе, [И] данные исследования, [Б] блог агентства/вендора, не проверено, [В] мой вывод.

## (а) Главные выводы

1. **Реклама в Telegram формально вне закона, срок отсрочки истекает 31.12.2026.** РКН подтвердил замедление 10.02.2026 [4]. ФАС в марте 2026 отнесла рекламу в Telegram и YouTube к запрету ч. 10.7 ст. 5 закона «О рекламе», но обещала не наказывать до конца 2026 [1][2][3]. На 9.11.2026 нового срока нет [5][Б]. Посевы и Telegram Ads нельзя закладывать в план 2027 [В].
2. **Свой канал и бот, по комментариям юристов, рекламным размещением не считаются** [6][Б]. Прямого текста ФАС об этом я не нашёл. Бот стоит строить «MAX первым, Telegram вторым», а QR в брошюрах вести на свою страницу-развилку, а не в мессенджер [В].
3. **MAX обошёл Telegram по месячной аудитории в июне 2026** (Mediascope в пересказе) [7]. С октября Mediascope скрыл охваты, а данные за сентябрь противоречивы [8]. Собственного рекламного кабинета на май 2026 не было; продвижение каналов идёт через VK Рекламу (с 10.06.2026) и посевы [9][10][Б].
4. **Мерить внешний трафик на Wildberries стало труднее.** Раздел «Внешний трафик» с UTM отключён с 22.07.2026 [12][Б], бесплатные подменные артикулы отменены с 1.07 [13][Б]. Рабочая замена — промокоды продавца (запущены в январе 2026) [14][15]. На Ozon UTM-отчёт сохраняется [69][Б].
5. **Рынок вырос ценой, а не объёмом.** DSM Group за 2025: 236,9 млрд руб. (+24,9%), маркетплейсы 54,4 млрд, упаковки +1,3%, топ-10 производителей держат 48,3% [40][41][И]. Трафик дорожает, поэтому экономику определяет повторный заказ [В].
6. **Регуляторное давление на карточки растёт.** С 1.03.2026 СГР сверяется при вводе в оборот [35]; с 1.10.2026 маркетплейсы проверяют новые карточки, старые — до 29.03.2027 [36][37]. Чистые документы становятся условием присутствия, и их можно использовать как аргумент на посадочной [В].
7. **Поиск уходит в нейроответы.** Алиса AI отвечает на 44% запросов Яндекса (отчёт за III кв. 2026 в пересказе) [42]; в Вебмастере с 7.04.2026 есть отчёт по видимости в Алисе [43][Б]. Страница с документами и прямыми ответами работает и как GEO-актив [В].
8. **В США растут два канала:** специалисты (9,2% рынка добавок в 2024, прогноз роста выше 7% в год, NBJ [52][И]) и creator-affiliate (TikTok Shop, витамины и добавки: $784 млн за 52 недели до февраля 2026, NielsenIQ [54][И]). Российские аналоги второго — Ozon Blogger и Wibes [44][45].
9. **Категории создавали поставщики ингредиентов с доказательной базой или вирусные «лечебные» обещания.** Второй путь вам закрыт принципами и законом (раздел е).

## (б) Каналы РФ

| Канал | Применим к БАД | Ограничения | Как мерить | Надёжность |
|---|---|---|---|---|
| Яндекс Директ, ПромоСтраницы | Да | Дисклеймер, СГР по запросу, проверка посадочной, без лечебных формулировок [20][Б] | Метрика; в кампании «Продажи на маркетплейсах» данные о заказах только для Ozon и Маркета [16][17] | Правила — блоги; про маркетплейсы — Яндекс |
| VK Реклама | Да | Дисклеймер не менее 10% площади, документы через поддержку [18][19]; 18+ [Б] | Пиксель, подписки | Справка VK (в сниппете) |
| MAX: канал, бот | Да | Бот только у верифицированного юрлица/ИП, модерация до 48 ч [11][Б] | Подписки, запуски бота | Блоги |
| Посевы в Telegram, Telegram Ads | До 31.12.2026 | См. вывод 1; erid обязателен [33] | Промокод, ссылка | СМИ со ссылкой на ФАС |
| Instagram и др. заблокированные | Нет | Запрет с 1.09.2025 [27][28] | — | [З] в пересказе |
| Блогеры (VK, Дзен, MAX) | Да | 10 тыс.+ только из реестра РКН; риск и для рекламодателя [31][32] | Промокод на автора | СМИ |
| Внутренняя реклама WB/Ozon | Да | ДРР считать от маржи; WB учитывает заказы до 14 дней после клика [65][Б] | Кабинет | Блоги |
| Ozon Blogger, Wibes (CPO) | Да | Ozon: самозанятые, порога подписчиков нет, с мая 2026 VK и MAX [44]; Wibes: 10% с продавца [45] | Кабинет площадки | СМИ; ставки расходятся |
| SEO / GEO | Да | Только нелечебные формулировки | Вебмастер (Алиса AI), ручной список промптов [43] | Блоги |
| Врачи | Ограниченно | Назначать можно только БАД из перечня Минздрава [21][22]; есть ли перечень сейчас — не подтверждено | Промокод, анкета | [З] в пересказе |
| Вкладыши | С оговорками | WB: штраф 50 000 руб. за вкладыш с вознаграждением за отзыв [46][Б]; про внешние QR блоги расходятся | QR с меткой | Официальных правил не нашёл |
| CPA-сети вне площадок | Не рекомендую | Формат связан с арбитражем «нутры» и обходом модерации [Б: https://vc.ru/marketing/2620745-reklama-badov-v-yandeks-direkt] | — | [В] |

## (в) Регуляторика

- **Реклама БАД (ст. 25 38-ФЗ).** Предупреждение «не является лекарственным средством» обязательно в каждом случае (ч. 1.1) [25][26]. Размер 10% площади подтверждён только справкой VK [18]; текст закона я не открыл. Запреты на отсылки к излечению и благодарности граждан известны мне по редакции закона, в этой сессии не сверены.
- **150-ФЗ от 07.06.2025 (с 1.09.2025).** Врачи вправе назначать зарегистрированные БАД из перечня; запрещена продажа незарегистрированных; сайты блокируются внесудебно — предписание РКН исполняется за 24 часа; действует и для маркетплейсов [21][22][23]. Порядок назначения был проектом в октябре 2025 [24]; итоговый приказ не нашёл.
- **Критерии качества БАД:** ПП № 398 от 13.04.2026, с 1.05.2026 [38]. Содержание не проверено.
- **Заблокированные и нежелательные площадки:** 72-ФЗ, ч. 10.7 ст. 5, с 1.09.2025; штраф за каждый пост [27][28]. Про Telegram и YouTube — вывод 1.
- **Маркировка рекламы:** erid через ОРД, пометка «Реклама», сведения о рекламодателе, отчётность в ЕРИР после размещения [33][Б].
- **Сбор 3%:** 479-ФЗ, ст. 18.2, с 1.04.2025, ПП № 1224 от 15.08.2025. Платят распространители, операторы и посредники; рекламодатель — при оплате иностранному лицу [29][30].
- **Реестр блогеров:** 303-ФЗ; реклама у незарегистрированных с 10 тыс.+ запрещена [31][32]. Дату начала запрета (в источниках 1.01.2025) по закону не сверял.
- **«Честный знак»:** перечень расширен ПП № 1953 от 28.11.2025 с 1.03.2026; остатки — до 31.08.2026 (срок годности до 3 лет) и до 31.08.2027 [34][35]. Источники расходятся в деталях.
- **289-ФЗ о платформенной экономике:** с 1.10.2026 [36]. Номер и дата постановления о проверке карточек расходятся: № 821 от 02.07.2026 [37] или № 504 от 30.04.2026 [36].
- **152-ФЗ:** локализация (23-ФЗ, с 1.07.2025), согласие отдельным документом с 1.09.2025 [39][Б]. Подтверждено слабо. Бот, собирающий контакты, делает завод оператором ПДн [В].

## (г) Модели лидогенерации

1. **Специалисты как канал.** США: Fullscript заявляет более 70 тыс. практиков (данные компании) [53]; Thorne вырос из этого канала и после кампании узнаваемости дал +63% в DTC [68]. РФ: «Эвалар» инициировал встречу с научным сообществом по назначению БАД [67]. Вам доступны материалы для специалистов и именной промокод без обещаний эффекта [В].
2. **Доказательность как лид-магнит.** Ritual: страница Made Traceable (2022) и обязательство провести клинические испытания всех продуктов к 2030 [56]. Это прямой аналог вашей страницы с документами.
3. **Квиз → база.** iTAB: около 6% прошедших тест возвращаются и покупают [48][Б]. Обратный пример — Care/of: Bayer купил 70% за $225 млн, в июне 2024 сервис закрыт [57]. Квиз годится как вход, но не как бизнес-модель [В].
4. **Бот и база под повторный заказ.** Кейс UGC для БАД: база 1700 контактов, около 30% заказывают раз в 1–2 месяца [49][Б]. Косметический бот: +20% повторных покупок [50][Б]. США: отток подписок 8–12% в месяц, CAC $80–130 [58][Б]. Цифры ориентировочные.
5. **Авторы с оплатой за заказ.** Goli и TikTok Shop [54]; в РФ — Ozon Blogger и Wibes [44][45].
6. **Длинный доверительный формат.** AG1 рано вложился в подкасты и долгие отношения с ведущими (интервью CMO, Wharton) [55]; оценки бюджета взяты из блогов. В РФ — ПромоСтраницы, кейс БАД на 500 тыс. пользователей [51][Б].
7. **Отзывы через инструменты площадок.** WB «Баллы за отзывы»; Ozon «Ускоренный сбор отзывов», 250 руб. за отзыв с 1.06.2026 [47][Б]. Вознаграждение в обход площадки наказывается [46].

## (д) Как мерить при продаже через маркетплейс

- **WB:** отдельный промокод продавца на канал или автора; срок до 60 дней, поэтому нужна ротация [15][Б]. Есть ли отчёт по каждому промокоду, не подтверждено.
- **Ozon:** UTM-отчёт в аналитике продавца; оплата за заказ в Директе [16][69].
- **Своя сторона:** страница-развилка с кнопками «WB / Ozon» даёт измеримые клики; в боте — дата покупки со слов клиента, напоминание и реферальный код [В].
- **Контроль:** сверять всплески заказов с датами размещений. Точность UTM-отчёта WB один селлер оценивал в 60–70% [Б: https://vc.ru/marketplace/2155450-otslezhivanie-prodazh-s-vneshney-reklamy-dlya-wildberries-i-ozon].
- **Недельный ритм** [В]: (1) охват и клики по каналам; (2) подписки в боте и цена подписчика; (3) клики на карточку; (4) заказы по промокодам и UTM, выкуп; (5) ДРР к марже; (6) доля повторных по когортам на 30/60/90 дней; (7) число рефералов. Целевых значений не даю: надёжных публичных бенчмарков для РФ я не нашёл.

## (е) Категорийный маркетинг

- **Ашваганда.** Категорию сделал поставщик брендированного экстракта KSM-66: 93% продаж брендированных экстрактов, более 4500 брендов (спонсорский материал) [59]. Рост в массовом канале: +185% в 2020, $176 млн за год до ноября 2025 [59][И]. Урок: инвестировать в исследования и стандарт ингредиента, а не только в банку.
- **Берберин.** $350 тыс. в месяц в 2022 → около $850 тыс. к лету 2023 после TikTok; ярлык «природный Оземпик» отраслевая пресса называет неточным и незаконным [60][И]. Для вас неприменимо.
- **Коллаген.** Vital Proteins: 2013 год, более $100 млн за четыре года, доля Nestlé в 2020, Дженнифер Энистон — ноябрь 2020 [61]. Категорию закрепил капитал.
- **NMN.** FDA исключило его из добавок в 2022 и вернуло 29.09.2025 [62]. Категория без регуляторной опоры уязвима.
- **Чага.** Four Sigmatic (2012): привычный носитель (кофе) и история происхождения; 200–300 млн чашек по словам самой компании [63].
- **Магний:** категорийных данных не нашёл, есть только рост линейки одного бренда на 16,55% за 2025 [64].
- **Небольшому производителю доступно** [В]: имя ингредиента плюс открытое досье (СГР, протоколы, происхождение сырья); один повод к употреблению; привычный формат; специалисты; поставка сырья другим брендам. Горизонт по примерам — 5–10 лет.

## Типичные ошибки

- Реклама на неготовую карточку: ДРР 30–50% [65][Б].
- Одна кампания на артикулы с разной маржой; оценка раньше 14 дней [65][Б].
- Ставка на один мессенджер [В].
- Вкладыш «подарок за отзыв» [46].
- Блогер вне реестра РКН или без erid [31][33].
- Оплата трафика без способа атрибуции на WB [12].
- Бюджет в посевы без сбора базы: при росте рынка ценой платить придётся снова [В].

## (ж) Что не удалось проверить

- Тексты ст. 5, 18.1, 18.2 и 25 закона «О рекламе», 150-ФЗ, 289-ФЗ, 152-ФЗ; части ст. 14.3 КоАП и размеры штрафов.
- Первоисточник разъяснений ФАС от 10 и 25.03.2026; статус рекламы в Telegram после 31.12.2026; квалификация собственного бота.
- Правила Яндекс Директа по БАД; оферты WB и Ozon о вкладышах и внешних QR; отчётность по промокодам WB; официальное подтверждение отключения «Внешнего трафика».
- Принят ли перечень БАД для назначения врачами и приказ Минздрава.
- Содержание ПП № 398 и № 821 (или № 504).
- Рекламный кабинет MAX на ноябрь 2026; лимиты рассылок ботов; актуальные охваты мессенджеров.
- Стоимость клика и доля повторных заказов по БАД на маркетплейсах в РФ.
- Данные NBJ/SPINS по магнию; выручка AG1 и Fullscript.
- Правовой статус нутрициологов как канала; любые данные о бетулине как категории.

## (з) Источники

1. https://pravo.ru/news/262958/
2. https://rb.ru/news/fas-dala-oficialnoe-razyasnenie-za-reklamu-v-telegram-i-youtube-ne-budut-shtrafovat-do-2027-goda/
3. https://ria.ru/20260310/fas-2079705199.html
4. https://www.rbc.ru/technology_and_media/10/02/2026/698b21a39a79473017a3cb4a
5. https://marketly.ru/blog/shtrafy-za-reklamu-v-telegram-2027
6. https://www.sostav.ru/blogs/287862/111618
7. https://techora.ru/news/max-vpervye-oboshel-telegram-po-mesyachnoy-2026-07-24
8. https://www.cnews.ru/news/top/2026-10-20_vpervye_za_god_blokirovok
9. https://ppc.world/articles/reklama-v-max-razbor-vozmozhnostey-i-rukovodstvo-dlya-reklamodateley/
10. https://www.sostav.ru/blogs/288427/82781
11. https://bothelp.io/ru/blog/kak-sozdat-bota-v-max-dlya-avtomatizaczii-biznesa ; https://www.smartbotpro.ru/blog/max-dlya-biznesa-vozmozhnosti-i-kak-sozdat-chat-bota
12. https://mobz.io/en/blog/wildberries-otklyuchaet-razdel-vneshniy-trafik-chto-delat-selleram-i-pochemu-mobzio-prodolzhaet-schitat-konversii-mobzio
13. https://selsup.ru/blog/wildberries-otmenyaet-besplatnye-podmennye-artikuly-s-1-iyulya-chto-delat-prodavtsam/
14. https://www.retail.ru/news/wildberries-pozvolit-selleram-sozdavat-promokody-dlya-pokupateley-27-yanvarya-2026-273815/
15. https://secrets.tbank.ru/novosti/wb-promokody/
16. https://yard.yandex.ru/courses/direct-prodvinutyy/prodvizhenie-magazinov
17. https://b2b.yandex.ru/adv/edu/materials/prodazhi-na-marketpleysah-v-yandeks-direkte
18. https://ads.vk.ru/help/documents/faq_moderation
19. https://ads.vk.ru/help/documents/required_documents
20. https://www.sostav.ru/blogs/285527/72276
21. https://base.garant.ru/412133618/
22. https://www.consultant.ru/law/hotdocs/89627.html
23. https://www.lidings.com/ru/media/legalupdates/dietary_supplements/
24. https://pharmvestnik.ru/content/news/Minzdrav-Rossii-razrabotal-poryadok-naznacheniya-BAD-vrachami.html
25. https://br.fas.gov.ru/generate_pdf/d9e48f24-2db9-4fca-8684-006e68b102d6
26. https://www.consultant.ru/law/podborki/reklama_bad/
27. https://t-j.ru/ads-ban/
28. https://garant.ru/products/ipo/prime/doc/412300256
29. https://kontur.ru/articles/190
30. https://robokassa.com/blog/articles/sbor-3-s-internet-reklamy/
31. https://companies.rbc.ru/news/kpq9MjVs2q/reklama-u-blogerov-s-10-000-podpischikov-kogda-biznesu-grozit-shtraf/
32. https://ppc.world/news/v-mincifry-dali-podrobnye-razyasneniya-pravil-registracii-blogerov-v-reestre-rkn/
33. https://www.sostav.ru/blogs/285528/85619 ; https://vc.ru/marketing/2853068-markirovka-reklamy-v-telegram
34. https://markirovka.ru/knowledge/tovarnye-gruppy/badi/sroki-i-etapy-zapuska-obyazatelnoy-markirovki-bad
35. https://www.retail.ru/news/rynok-bad-s-1-marta-zhdet-rasshirenie-markirovki-i-usilenie-kontrolya-onlayn-pro-27-fevralya-2026-275028/ ; https://rg.ru/2026/03/01/nachali-dejstvovat-novye-pravila-prodazhi-bad.html
36. https://www.tks.ru/practicum/2026/09/16/01/s-1-oktyabrya-2026-goda-marketplejsyi-nachnut-proveryat-kartochki-tovarov-po-novyim-pravilam/
37. https://incrussia.ru/news/proizvoditeli-badov-potrebovali-rasshirit-kontrol-za-tovarami-na-marketplejsah/
38. https://companies.rbc.ru/news/qX6kvtweKM/chetyire-kriteriya-kachestva-bad-chto-izmenilos-s-1-maya-2026-goda/
39. https://habr.com/ru/articles/925642/ ; https://workspace.ru/blog/personalnye-dannye-2025-uvedomlenie-roskomnadzora-trebuet-menyat-sayty-a-kak/
40. https://incrussia.ru/understand/vitaminki-2/
41. https://logistics.ru/internet-torgovlya-i-fulfilment-riteyl/rynok-badov-rost-na-chetvert-v-dengakh-i-novyy-vyzov-dlya
42. https://habr.com/ru/articles/1104954/
43. https://optimism.ru/blog/generativnaya-optimizaciya-geo/
44. https://rb.ru/news/ozon-zapustil-partnyorskuyu-programmu-dlya-avtorov-blogery-v-max-i-vk-smogut-zarabatyvat-na-rekomendaciyah-tovarov/
45. https://e-pepper.ru/blogs/news/wibes-uvelichivaet-vyplaty-blogeram-v-partnerskoy-programme ; https://blog.click.ru/market-news/wildberries-vnedrila-monetizaciyu-dlya-blogerov-v-prilozhenie-wibes/
46. https://vc.ru/marketing/1226938-shtrafy-na-wildberries-i-kak-ih-izbezhat ; https://secrets.tbank.ru/razvitie/shtrafy-na-marketpleysakh/
47. https://uniseller.io/blog/kak-poluchit-pervye-otzyvy-na-wb-i-ozon-bez-blokirovki/
48. https://ratingruneta.ru/cases/case-14312/
49. https://blog.polushkoagency.ru/keis-kontent-zavod-ugc-dlya-badov/
50. https://bothelp.io/ru/blog/keys-chat-bot-dlya-kosmeticheskoy-kompanii
51. https://vc.ru/marketing/1458781-kak-privesti-k-brendu-500k-polzovatelei-cherez-promostranicy-keis-prodvizheniya-badov
52. https://www.nutraingredients.com/Article/2025/11/03/supplements-in-the-health-care-practitioner-channel-a-gate-kept-growth-area
53. https://fullscript.com/company-news/fullscript-completes-acquisition-of-emerson-ecologics
54. https://www.nutraingredients.com/Article/2026/06/23/tiktok-shops-largest-health-beauty-category-supplements/
55. https://knowledge.wharton.upenn.edu/podcast/marketing-matters/how-ag1-built-trust-through-podcast-marketing/
56. https://www.modernretail.co/operations/ritual-vitamins-wants-traceability-to-become-the-new-transparency/
57. https://www.nutraingredients.com/Article/2024/06/07/Care-of-to-close-operations/
58. https://eightx.co/blog/supplement-cac-payback-benchmarks ; https://eightx.co/blog/supplements-subscription-economics
59. https://www.vitafoodsinsights.com/botanicals-herbs/ashwagandha-from-ayurvedic-medicine-to-star-of-the-mainstream ; https://www.supplysidesj.com/supplements/ashwagandha-goes-mainstream-in-u-s-as-sales-boom ; https://www.supplysidesj.com/herbs-botanicals/trusted-and-tested-the-record-behind-ksm-66-ashwagandha
60. https://www.nutraingredients.com/Article/2023/07/14/The-skinny-on-berberine-Is-it-really-naturesozempic/ ; https://www.nutraceuticalsworld.com/exclusives/berberine-is-not-natures-ozempic-but-its-fame-is-far-from-over/
61. https://www.foodbusinessnews.net/articles/20738-nestle-finalizes-acquisition-of-vital-proteins ; https://www.forbes.com/sites/yolarobert1/2020/06/11/nestl-health-science-acquires-vital-proteins/
62. https://www.venable.com/insights/publications/2025/10/fda-declares-nicotinamide-mononucleotide-is
63. https://www.wikiwand.com/en/articles/Four_Sigmatic ; https://www.bevindustry.com/articles/97836-four-sigmatic-embraces-finlands-mushroom-coffee-culture
64. https://www.modernretail.co/operations/inside-magnesiums-rise-as-the-star-of-the-supplement-aisle/
65. https://secrets.tbank.ru/razvitie/oshibki-sellerov/ ; https://dipustovalov.ru/blog/wildberries-ozon-marketing-2026
66. https://elama.ru/blog/zapret-reklamy-v-telegram/
67. https://pharmvestnik.ru/content/news/evalar-iniciiroval-vstrechu-s-liderami-nauchnogo-soobshestva-po-voprosu-o-naznachenii-bad-vrachami.html
68. https://www.modernretail.co/marketing/how-thorne-drove-63-growth-in-dtc-sales-after-a-brand-awareness-push/
69. https://vc.ru/marketplace/2155450-otslezhivanie-prodazh-s-vneshney-reklamy-dlya-wildberries-i-ozon
