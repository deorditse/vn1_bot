import textwrap

menu_example = textwrap.dedent('''
<li>
  <a href="#Описание препарата" class="product-details-instructions-main__menu-item">
    Описание препарата
  </a>
</li>
<li>
  <a href="#Форма выпуска и состав" class="product-details-instructions-main__menu-item">
    Форма выпуска и состав
  </a>
</li>
<li>
  <a href="#Фармакологическое действие" class="product-details-instructions-main__menu-item">
    Фармакологическое действие
  </a>
</li>
<li>
  <a href="#Фармакодинамика" class="product-details-instructions-main__menu-item">
    Фармакодинамика
  </a>
</li>
<li>
  <a href="#Фармакокинетика" class="product-details-instructions-main__menu-item">
    Фармакокинетика
  </a>
</li>
<li>
  <a href="#Показания к применению" class="product-details-instructions-main__menu-item">
    Показания к применению
  </a>
</li>
<li>
  <a href="#Противопоказания" class="product-details-instructions-main__menu-item">
    Противопоказания
  </a>
</li>
<li>
  <a href="#Побочные эффекты" class="product-details-instructions-main__menu-item">
    Побочные эффекты
  </a>
</li>
<li>
  <a href="#Как принимать и дозировка" class="product-details-instructions-main__menu-item">
    Как принимать и дозировка
  </a>
</li>
<li>
  <a href="#Передозировка" class="product-details-instructions-main__menu-item">
    Передозировка
  </a>
</li>
<li>
  <a href="#Взаимодействие с другими препаратами" class="product-details-instructions-main__menu-item">
    Взаимодействие с другими препаратами
  </a>
</li>
<li>
  <a href="#Аналоги Бифиформ" class="product-details-instructions-main__menu-item">
    Аналоги Бифиформ
  </a>
</li>
<li>
  <a href="#Можно ли принимать детям" class="product-details-instructions-main__menu-item">
    Можно ли принимать детям
  </a>
</li>
<li>
  <a href="#Можно ли принимать Бифиформ при беременности и кормлении грудью" class="product-details-instructions-main__menu-item">
    Можно ли принимать Бифиформ при беременности и кормлении грудью
  </a>
</li>
<li>
  <a href="#Совместим ли Бифиформ и алкоголь" class="product-details-instructions-main__menu-item">
    Совместим ли Бифиформ и алкоголь
  </a>
</li>
<li>
  <a href="#Отпускается по рецепту или нет" class="product-details-instructions-main__menu-item">
    Отпускается по рецепту или нет
  </a>
</li>
<li>
  <a href="#Как хранить Бифиформ" class="product-details-instructions-main__menu-item">
    Как хранить Бифиформ
  </a>
</li>
<li>
  <a href="#Срок годности" class="product-details-instructions-main__menu-item">
    Срок годности
  </a>
</li>
<li>
  <a href="#Производитель" class="product-details-instructions-main__menu-item">
    Производитель
  </a>
</li>
<li><a href="#Источники" class="product-details-instructions-main__menu-item">Источники</a></li>
''').strip()

content_example = textwrap.dedent('''              
<li class="product-details-instructions-main__item open" id="in-Описание препарата">
  <div class="product-details-instructions-main__item-questions">
    <h3 id="Описание препарата">Описание препарата</h3>
    <div class="product-details-instructions-main__item--arrow"></div>
  </div>
  <div class="product-details-instructions-main__item-answer">
    <p><strong>Бифиформ</strong> — это препарат, содержащий симбиотические бактерии, предназначенный для нормализации микрофлоры кишечника. Применяется для профилактики и лечения дисбактериозов, 
    а также для поддержания иммунной системы. Действующие вещества препарата — <em>Bifidobacterium longum</em> и <em>Enterococcus faecium</em> — обеспечивают высокую антагонистическую активность против патогенных микроорганизмов, 
    нормализуют пищеварительные функции кишечника.</p>
  </div>
</li>
<li class="product-details-instructions-main__item open" id="in-Форма выпуска и состав">
  <div class="product-details-instructions-main__item-questions">
    <h3 id="Форма выпуска и состав">Форма выпуска и состав</h3>
    <div class="product-details-instructions-main__item--arrow"></div>
  </div>
  <div class="product-details-instructions-main__item-answer">
    <p><strong>Бифиформ</strong> доступен в нескольких формах выпуска:</p>
    <ul>
      <li><strong>Капсулы кишечнорастворимые</strong>: каждая капсула содержит <em>Enterococcus faecium ENCfa-68</em> и <em>Bifidobacterium longum ВВ-46</em> (по не менее 1×10^7 КОЕ).</li>
      <li><strong>Бифиформ Кидс таблетки жевательные</strong>: каждая таблетка содержит <em>Lactobacillus rhamnosus LGG</em> и <em>Bifidobacterium animalis BB-12</em>, а также витамины группы В — тиамин и пиридоксин.</li>
    </ul>
    <p>Каждая форма содержит вспомогательные компоненты, такие как декстроза, магний стеарат, лактулоза, а также оболочку капсул и добавки в жевательных таблетках (ароматизаторы, глицерил бегенат, фруктоолигосахариды).</p>
  </div>
</li>
<li class="product-details-instructions-main__item open" id="in-Фармакологическое действие">
  <div class="product-details-instructions-main__item-questions">
    <h3 id="Фармакологическое действие">Фармакологическое действие</h3>
    <div class="product-details-instructions-main__item--arrow"></div>
  </div>
  <div class="product-details-instructions-main__item-answer">
    <p><strong>Бифиформ</strong> — эубиотик, нормализующий баланс микрофлоры кишечника. Его компоненты — <em>Bifidobacterium longum</em> и <em>Enterococcus faecium</em> — 
    обеспечивают антагонистическую активность против патогенных и условно-патогенных микроорганизмов, способствуют нормализации пищеварения и поддержанию иммунной системы. 
    Также они ингибируют транслокацию бактерий в кишечнике, улучшая барьерные функции слизистой.</p>
  </div>
</li>
<li class="product-details-instructions-main__item open" id="in-Фармакодинамика">
  <div class="product-details-instructions-main__item-questions">
    <h3 id="Фармакодинамика">Фармакодинамика</h3>
    <div class="product-details-instructions-main__item--arrow"></div>
  </div>
  <div class="product-details-instructions-main__item-answer">
    <p>Бифидобактерии и энтерококки в составе препарата оказывают положительное воздействие на кишечную микрофлору, регулируя её состав и повышая устойчивость слизистой оболочки кишечника. Это способствует улучшению состояния как толстого, так и тонкого кишечника, особенно при наличии диспепсии и метеоризма.</p>
  </div>
</li>
<li class="product-details-instructions-main__item open" id="in-Фармакокинетика">
  <div class="product-details-instructions-main__item-questions">
    <h3 id="Фармакокинетика">Фармакокинетика</h3>
    <div class="product-details-instructions-main__item--arrow"></div>
  </div>
  <div class="product-details-instructions-main__item-answer">
    <p>Из-за того, что Бифиформ работает непосредственно в кишечнике и не всасывается в кровь, фармакокинетика препарата не имеет значимых характеристик для системного эффекта. 
    Компоненты препарата действуют локально, поддерживая микрофлору кишечника и не оказывая системного воздействия.</p>
  </div>
</li>
<li class="product-details-instructions-main__item open" id="in-Показания к применению">
  <div class="product-details-instructions-main__item-questions">
    <h3 id="Показания к применению">Показания к применению</h3>
    <div class="product-details-instructions-main__item--arrow"></div>
  </div>
  <div class="product-details-instructions-main__item-answer">
    <p><strong>Бифиформ</strong> применяется для лечения и профилактики:</p>
    <ul>
      <li>Дисбактериозов кишечника различной этиологии.</li>
      <li>Диарей, включая вирусные и антибиотик-ассоциированные.</li>
      <li>Синдрома раздраженного кишечника.</li>
      <li>Метеоризма и других расстройств пищеварения.</li>
      <li>Профилактики антибиотик-ассоциированной диареи.</li>
      <li>Поддержания иммунной системы.</li>
    </ul>
    <p>Препарат помогает восстановить нормальный баланс кишечной микрофлоры и улучшить функции желудочно-кишечного тракта.</p>
  </div>
</li>
<li class="product-details-instructions-main__item open" id="in-Противопоказания">
  <div class="product-details-instructions-main__item-questions">
    <h3 id="Противопоказания">Противопоказания</h3>
    <div class="product-details-instructions-main__item--arrow"></div>
  </div>
  <div class="product-details-instructions-main__item-answer">
    <p>Противопоказаниями к применению Бифиформа являются:</p>
    <ul>
      <li>Индивидуальная непереносимость компонентов препарата.</li>
      <li>Аллергические реакции на дрожжи или другие вспомогательные вещества.</li>
    </ul>
    <p>Применение с осторожностью при наличии непереносимости фруктозы, сахаразы/изомальтазы, а также в случае глюкозо-галактозной мальабсорбции.</p>
  </div>
</li>
<li class="product-details-instructions-main__item open" id="in-Побочные эффекты">
  <div class="product-details-instructions-main__item-questions">
    <h3 id="Побочные эффекты">Побочные эффекты</h3>
    <div class="product-details-instructions-main__item--arrow"></div>
  </div>
  <div class="product-details-instructions-main__item-answer">
    <p>При применении Бифиформа в рекомендованных дозах побочные эффекты не наблюдаются. 
    Препарат считается безопасным для применения в терапевтических дозах, при этом могут возникать индивидуальные реакции, такие как легкая тошнота или метеоризм.</p>
  </div>
</li>
<li class="product-details-instructions-main__item open" id="in-Как принимать и дозировка">
  <div class="product-details-instructions-main__item-questions">
    <h3 id="Как принимать и дозировка">Как принимать и дозировка</h3>
    <div class="product-details-instructions-main__item--arrow"></div>
  </div>
  <div class="product-details-instructions-main__item-answer">
    <p>Бифиформ рекомендуется принимать внутрь:</p>
      <ul>
        <li><strong>Взрослым</strong> и детям старше 12 лет: по 1 капсуле 2-3 раза в день.</li>
        <li><strong>Детям от 2 лет</strong>: по 1 капсуле 2-3 раза в день. Если ребенок не может проглотить капсулу, содержимое можно развести в небольшой дозе жидкости.</li>
      </ul>
    <p><strong>Бифиформ Кидс:<strong></strong></strong></p><strong><strong>
      <ul>
        <li>Детям от 3 лет: по 1 таблетке 2 раза в день.</li>
      </ul>
    <p>Дозировка и продолжительность приема могут быть скорректированы врачом в зависимости от состояния пациента.</p>
  </strong></strong></div><strong><strong>
</strong></strong></li><strong><strong>
<li class="product-details-instructions-main__item open" id="in-Передозировка">
  <div class="product-details-instructions-main__item-questions">
    <h3 id="Передозировка">Передозировка</h3>
    <div class="product-details-instructions-main__item--arrow"></div>
  </div>
  <div class="product-details-instructions-main__item-answer">
    <p>Передозировка Бифиформом не приводит к тяжелым последствиям, так как препарат действует только локально в кишечнике. В случае значительного превышения дозы рекомендуется медицинское наблюдение.</p>
  </div>
</li>
<li class="product-details-instructions-main__item open" id="in-Взаимодействие с другими препаратами">
  <div class="product-details-instructions-main__item-questions">
    <h3 id="Взаимодействие с другими препаратами">Взаимодействие с другими препаратами</h3>
    <div class="product-details-instructions-main__item--arrow"></div>
  </div>
  <div class="product-details-instructions-main__item-answer">
    <p>Бифиформ можно принимать одновременно с антибиотиками для профилактики антибиотик-ассоциированной диареи. 
    Препарат не взаимодействует с другими лекарственными средствами, так как действует локально и не всасывается в кровь.</p>
    <table>
 <tbody>
 <tr>
 <td>
 <p><strong>Взаимодействие</strong></p>
 </td>
 <td>
 <p><strong>Другие лекарственные препараты</strong></p>
 </td>
 </tr>
 <tr>
 <td>
 <p>Стимулирование синтеза гидроксилированных активных метаболитов, что приводит к тяжелым интоксикациям.</p>
 </td>
 <td>
 <p>Индукторы ферментов микросомального окисления в печени: фенитоин, этанол, барбитураты, флумецинол, рифампицин, фенилбутазон, трициклические антидепрессанты.</p>
 </td>
 </tr>
 <tr>
 <td>
 <p>Минимизация вероятности формирования гепатотоксического эффекта.</p>
 </td>
 <td>
 <p>Ингибиторы микросомального окисления.</p>
 </td>
 </tr>
 <tr>
 <td>
 <p>Ибупрофен оказывает негативное влияние на эффективность работы указанных средств.</p>
 </td>
 <td>
 <p>Вазодилататоры, фуросемид, гидрохлоротиазиды, урикозурические препараты.</p>
 </td>
 </tr>
 <tr>
 <td>
 <p>Повышение риска возникновения кровотечений.</p>
 </td>
 <td>
 <p>Антикоагулянты, антиагреганты, фибринолитики.</p>
 </td>
 </tr>
 <tr>
 <td>
 <p>Потеря эффективности Ибупрофена.</p>
 </td>
 <td>
 <p>Антациды.</p>
 </td>
 </tr>
 <tr>
 <td>
 <p>Повышение риска возникновения желудочно-кишечных кровотечений.</p>
 </td>
 <td>
 <p>Минералокортикостероиды, глюкокортикостероиды, этанол.</p>
 </td>
 </tr>
 <tr>
 <td>
 <p>Усиление гипогликемического эффекта.</p>
 </td>
 <td>
 <p>Производные сульфонилмочевины.</p>
 </td>
 </tr>
 <tr>
 <td>
 <p>Риск возникновения и выраженность побочных эффектов.</p>
 </td>
 <td>
 <p>Два и более НПВП.</p>
 </td>
 </tr>
 <tr>
 <td>
 <p>Усиление обезболивающего действия.</p>
 </td>
 <td>
 <p>Кофеин.</p>
 </td>
 </tr>
 <tr>
 <td>
 <p>Снижение противовоспалительного и антиагрегантного действия лекарственного препарата.</p>
 </td>
 <td>
 <p>Салицилаты.</p>
 </td>
 </tr>
 <tr>
 <td>
 <p>Повышается вероятность развития гипотромбинемии.</p>
 </td>
 <td>
 <p>Цефамандол, цефоперазон, цефотетан, вальпроевая кислота, пликамицин.</p>
 </td>
 </tr>
 <tr>
 <td>
 <p>Повышение гематотоксичности Ибупрофена.</p>
 </td>
 <td>
 <p>Миелотоксические лекарственные средства.</p>
 </td>
 </tr>
 <tr>
 <td>
 <p>Стимулирование эффекта ибупрофена.</p>
 </td>
 <td>
 <p>Циклоспорин и препараты с содержанием золота.</p>
 </td>
 </tr>
 <tr>
 <td>
 <p>Снижение скорости выведения ибупрофена и повышение его концентрации в крови.</p>
 </td>
 <td>
 <p>Блокаторы кальциевых канальцев.</p>
 </td>
 </tr>
 </tbody>
 </table>
  </div>
</li>
<li class="product-details-instructions-main__item open" id="in-Аналоги Бифиформ">
  <div class="product-details-instructions-main__item-questions">
    <h3 id="Аналоги Бифиформ">Аналоги Бифиформ</h3>
    <div class="product-details-instructions-main__item--arrow"></div>
  </div>
  <div class="product-details-instructions-main__item-answer">
    <p>Структурных аналогов Бифиформ с точно таким же МНН нет. Однако на рынке имеются <a href="https://vn1.ru/selection/bifiform/analogues/" target="_blank">другие препараты</a> с похожим действием, содержащие пробиотики и симбиотики, которые может назначить врач.</p>
  </div>
</li>
<li class="product-details-instructions-main__item open" id="in-Можно ли принимать детям">
  <div class="product-details-instructions-main__item-questions">
    <h3 id="Можно ли принимать детям">Можно ли принимать детям</h3>
    <div class="product-details-instructions-main__item--arrow"></div>
  </div>
  <div class="product-details-instructions-main__item-answer">
    <p>Бифиформ можно применять у детей с 2 лет. Детям младше 2 лет препарат не рекомендуется без консультации с врачом.</p>
  </div>
</li>
<li class="product-details-instructions-main__item open" id="in-Можно ли принимать Бифиформ при беременности и кормлении грудью">
  <div class="product-details-instructions-main__item-questions">
    <h3 id="Можно ли принимать Бифиформ при беременности и кормлении грудью">Можно ли принимать Бифиформ при беременности и кормлении грудью</h3>
    <div class="product-details-instructions-main__item--arrow"></div>
  </div>
  <div class="product-details-instructions-main__item-answer">
    <p>Применение Бифиформа при беременности и лактации безопасно, так как препарат не всасывается и не оказывает системного воздействия.</p>
  </div>
</li>
<li class="product-details-instructions-main__item open" id="in-Совместим ли Бифиформ и алкоголь">
  <div class="product-details-instructions-main__item-questions">
    <h3 id="Совместим ли Бифиформ и алкоголь">Совместим ли Бифиформ и алкоголь</h3>
    <div class="product-details-instructions-main__item--arrow"></div>
  </div>
  <div class="product-details-instructions-main__item-answer">
    <p>Употребление алкоголя во время применения Бифиорма не противопоказано, так как препарат не оказывает системного воздействия и не взаимодействует с алкоголем.</p>
  </div>
</li>
<li class="product-details-instructions-main__item open" id="in-Отпускается по рецепту или нет">
  <div class="product-details-instructions-main__item-questions">
    <h3 id="Отпускается по рецепту или нет">Отпускается по рецепту или нет</h3>
    <div class="product-details-instructions-main__item--arrow"></div>
  </div>
  <div class="product-details-instructions-main__item-answer">
    <p>Бифиформ отпускается без рецепта.</p>
  </div>
</li>
<li class="product-details-instructions-main__item open" id="in-Как хранить Бифиформ">
  <div class="product-details-instructions-main__item-questions">
    <h3 id="Как хранить Бифиформ">Как хранить Бифиформ</h3>
    <div class="product-details-instructions-main__item--arrow"></div>
  </div>
  <div class="product-details-instructions-main__item-answer">
    <p>Препарат следует хранить при температуре не выше 25°C в сухом месте, недоступном для детей.</p>
  </div>
</li>
<li class="product-details-instructions-main__item open" id="in-Срок годности">
  <div class="product-details-instructions-main__item-questions">
    <h3 id="Срок годности">Срок годности</h3>
    <div class="product-details-instructions-main__item--arrow"></div>
  </div>
  <div class="product-details-instructions-main__item-answer">
    <p>Срок годности Бифиформа – 2 года. Не использовать после истечения срока годности.</p>
  </div>
</li>
<li class="product-details-instructions-main__item open" id="in-Производитель">
  <div class="product-details-instructions-main__item-questions">
    <h3 id="Производитель">Производитель</h3>
    <div class="product-details-instructions-main__item--arrow"></div>
  </div>
  <div class="product-details-instructions-main__item-answer">
    <p>Производителем Бифиформа является компания Pfizer Consumer Manufacturing Italy S R L, Италия. Производственная площадка (завод-производитель) может быть изменена держателем регистрационного удостоверения.</p>
  </div>
</li>                                                                        <li class="product-detail-item product-details-instructions-main__item open" id="in-sources">
                                        <div class="product-detail-item__question product-details-instructions-main__item-questions">
                                            <h3 id="Источники">Источники</h3>
                                            <div class="product-details-instructions-main__item--arrow"></div>
                                        </div>
                                        <div class="product-detail-item__answer-outer product-details-instructions-main__item-answer-outer">
                                            <div class="product-detail-item__answer product-details-instructions-main__item-answer">
                                                <ol class="product-sources__list">
                                                    <li class="product-sources__item"><a class="product-sources__link" target="_blank" href="https://grls.rosminzdrav.ru/default.aspx" rel="nofollow">Государственный
                                                            реестр лекарственных средств</a></li>
                                                    <li class="product-sources__item">Анатомо-терапевтическо-химическая
                                                        классификация (ATX)
                                                    </li>
                                                    <li class="product-sources__item">Международная классификация
                                                        болезней (МКБ-10)
                                                    </li>
                                                    <li class="product-sources__item">Официальная инструкция от
                                                        производителя
                                                    </li>
                                                </ol>
                                                                                                    <a href="/authors/akimova-elena-ivanovna/">
                                                        <div class="product_detail_verified product-verified" id="pharmacist_recommend">
                                                            <div class="product-verified__wrapper">
                                                                <div class="product-verified__image">
                                                                    <img src="/upload/iblock/dc2/akimova-elena-ivanovna_preview_143817.jpg" alt="" loading="lazy">
                                                                </div>
                                                                <div class="product-verified__content">
                                                                    <span class="product-verified__checked">Проверено фармацевтом</span>
                                                                    <span class="product-verified__fio">Акимова Елена Ивановна</span>
                                                                                                                                            <span class="product-verified__team-info">Фармацевт</span>
                                                                                                                                                                                                                <span class="product-verified__position">Стаж с 2009 года</span>
                                                                                                                                    </div>
                                                                <div class="product-verified__icon">
                                                                    <img alt="Проверено фармацевтом" class="product-verified__icon-img" src="/local/templates/.default/img/icon-verified.svg" loading="lazy">
                                                                </div>
                                                            </div>
                                                        </div>
                                                    </a>
                                                                                            </div>
                                        </div>
                                    </li>
</strong></strong>''').strip()

md_example = textwrap.dedent('''
**Бифиформ инструкция по применению**\n\n**Описание препарата**\n\n**Бифиформ** --- это препарат, содержащий симбиотические бактерии,\nпредназначенный для нормализации микрофлоры кишечника. Применяется для\nпрофилактики и лечения дисбактериозов, а также для поддержания иммунной\nсистемы. Действующие вещества препарата --- *Bifidobacterium longum* и\n*Enterococcus faecium* --- обеспечивают высокую антагонистическую\nактивность против патогенных микроорганизмов, нормализуют\nпищеварительные функции кишечника.\n\n**Форма выпуска и состав**\n\n**Бифиформ** доступен в нескольких формах выпуска:\n\n-   **Капсулы кишечнорастворимые**: каждая капсула содержит\n    *Enterococcus faecium ENCfa-68* и *Bifidobacterium longum ВВ-46* (по\n    не менее 1×10\^7 КОЕ).\n\n-   **Бифиформ Кидс таблетки жевательные**: каждая таблетка содержит\n    *Lactobacillus rhamnosus LGG* и *Bifidobacterium animalis BB-12*, а\n    также витамины группы В --- тиамин и пиридоксин.\n\nКаждая форма содержит вспомогательные компоненты, такие как декстроза,\nмагний стеарат, лактулоза, а также оболочку капсул и добавки в\nжевательных таблетках (ароматизаторы, глицерил бегенат,\nфруктоолигосахариды).\n\n**Фармакологическое действие**\n\n**Бифиформ** --- эубиотик, нормализующий баланс микрофлоры кишечника.\nЕго компоненты --- *Bifidobacterium longum* и *Enterococcus faecium* ---\nобеспечивают антагонистическую активность против патогенных и\nусловно-патогенных микроорганизмов, способствуют нормализации\nпищеварения и поддержанию иммунной системы. Также они ингибируют\nтранслокацию бактерий в кишечнике, улучшая барьерные функции слизистой.\n\n**Фармакодинамика**\n\nБифидобактерии и энтерококки в составе препарата оказывают положительное\nвоздействие на кишечную микрофлору, регулируя её состав и повышая\nустойчивость слизистой оболочки кишечника. Это способствует улучшению\nсостояния как толстого, так и тонкого кишечника, особенно при наличии\nдиспепсии и метеоризма.\n\n**Фармакокинетика**\n\nИз-за того, что Бифиформ работает непосредственно в кишечнике и не\nвсасывается в кровь, фармакокинетика препарата не имеет значимых\nхарактеристик для системного эффекта. Компоненты препарата действуют\nлокально, поддерживая микрофлору кишечника и не оказывая системного\nвоздействия.\n\n**Показания к применению**\n\n**Бифиформ** применяется для лечения и профилактики:\n\n-   Дисбактериозов кишечника различной этиологии.\n\n-   Диарей, включая вирусные и антибиотик-ассоциированные.\n\n-   Синдрома раздраженного кишечника.\n\n-   Метеоризма и других расстройств пищеварения.\n\n-   Профилактики антибиотик-ассоциированной диареи.\n\n-   Поддержания иммунной системы.\n\nПрепарат помогает восстановить нормальный баланс кишечной микрофлоры и\nулучшить функции желудочно-кишечного тракта.\n\n**Противопоказания**\n\nПротивопоказаниями к применению Бифиформа являются:\n\n-   Индивидуальная непереносимость компонентов препарата.\n\n-   Аллергические реакции на дрожжи или другие вспомогательные вещества.\n\nПрименение с осторожностью при наличии непереносимости фруктозы,\nсахаразы/изомальтазы, а также в случае глюкозо-галактозной\nмальабсорбции.\n\n**Побочные эффекты**\n\nПри применении Бифиформа в рекомендованных дозах побочные эффекты не\nнаблюдаются. Препарат считается безопасным для применения в\nтерапевтических дозах, при этом могут возникать индивидуальные реакции,\nтакие как легкая тошнота или метеоризм.\n\n**Как принимать и дозировка**\n\nБифиформ рекомендуется принимать внутрь:\n\n-   **Взрослым** и детям старше 12 лет: по 1 капсуле 2-3 раза в день.\n\n-   **Детям от 2 лет**: по 1 капсуле 2-3 раза в день. Если ребенок не\n    может проглотить капсулу, содержимое можно развести в небольшой дозе\n    жидкости.\n\n**Бифиформ Кидс**:\n\n-   Детям от 3 лет: по 1 таблетке 2 раза в день.\n\nДозировка и продолжительность приема могут быть скорректированы врачом в\nзависимости от состояния пациента.\n\n**Передозировка**\n\nПередозировка Бифиформом не приводит к тяжелым последствиям, так как\nпрепарат действует только локально в кишечнике. В случае значительного\nпревышения дозы рекомендуется медицинское наблюдение.\n\n**Взаимодействие с другими препаратами**\n\nБифиформ можно принимать одновременно с антибиотиками для профилактики\nантибиотик-ассоциированной диареи. Препарат не взаимодействует с другими\nлекарственными средствами, так как действует локально и не всасывается в\nкровь.\n\n  -----------------------------------------------------------------------\n  **Взаимодействие**              **Другие лекарственные препараты**\n  ------------------------------- ---------------------------------------\n  Стимулирование синтеза          Индукторы ферментов микросомального\n  гидроксилированных активных     окисления в печени: фенитоин, этанол,\n  метаболитов, что приводит к     барбитураты, флумецинол, рифампицин,\n  тяжелым интоксикациям.          фенилбутазон, трициклические\n                                  антидепрессанты.\n\n  Минимизация вероятности         Ингибиторы микросомального окисления.\n  формирования гепатотоксического \n  эффекта.                        \n\n  Ибупрофен оказывает негативное  Вазодилататоры, фуросемид,\n  влияние на эффективность работы гидрохлоротиазиды, урикозурические\n  указанных средств.              препараты.\n\n  Повышение риска возникновения   Антикоагулянты, антиагреганты,\n  кровотечений.                   фибринолитики.\n\n  Потеря эффективности            Антациды.\n  Ибупрофена.                     \n\n  Повышение риска возникновения   Минералокортикостероиды,\n  желудочно-кишечных              глюкокортикостероиды, этанол.\n  кровотечений.                   \n\n  Усиление гипогликемического     Производные сульфонилмочевины.\n  эффекта.                        \n\n  Риск возникновения и            Два и более НПВП.\n  выраженность побочных эффектов. \n\n  Усиление обезболивающего        Кофеин.\n  действия.                       \n\n  Снижение противовоспалительного Салицилаты.\n  и антиагрегантного действия     \n  лекарственного препарата.       \n\n  Повышается вероятность развития Цефамандол, цефоперазон, цефотетан,\n  гипотромбинемии.                вальпроевая кислота, пликамицин.\n\n  Повышение гематотоксичности     Миелотоксические лекарственные\n  Ибупрофена.                     средства.\n\n  Стимулирование эффекта          Циклоспорин и препараты с содержанием\n  ибупрофена.                     золота.\n\n  Снижение скорости выведения     Блокаторы кальциевых канальцев.\n  ибупрофена и повышение его      \n  концентрации в крови.           \n  -----------------------------------------------------------------------\n\n**Аналоги Бифиформ**\n\nСтруктурных аналогов Бифиформ с точно таким же МНН нет. Однако на рынке\nимеются [другие препараты](https://vn1.ru/selection/bifiform/analogues/)\nс похожим действием, содержащие пробиотики и симбиотики, которые может\nназначить врач.\n\n**Можно ли принимать детям**\n\nБифиформ можно применять у детей с 2 лет. Детям младше 2 лет препарат не\nрекомендуется без консультации с врачом.\n\n**Можно ли принимать Бифиформ при беременности и кормлении грудью**\n\nПрименение Бифиформа при беременности и лактации безопасно, так как\nпрепарат не всасывается и не оказывает системного воздействия.\n\n**Совместим ли Бифиформ и алкоголь**\n\nУпотребление алкоголя во время применения Бифиорма не противопоказано,\nтак как препарат не оказывает системного воздействия и не\nвзаимодействует с алкоголем.\n\n**Отпускается по рецепту или нет**\n\nБифиформ отпускается без рецепта.\n\n**Как хранить Бифиформ**\n\nПрепарат следует хранить при температуре не выше 25°C в сухом месте,\nнедоступном для детей.\n\n**Срок годности**\n\nСрок годности Бифиформа -- 2 года. Не использовать после истечения срока\nгодности.\n\n**Производитель**\n\nПроизводителем Бифиформа является компания Pfizer Consumer Manufacturing\nItaly S R L, Италия. Производственная площадка (завод-производитель)\nможет быть изменена держателем регистрационного удостоверения.
''').strip()
