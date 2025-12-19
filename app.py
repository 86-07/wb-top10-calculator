import streamlit as st
import pandas as pd
import numpy as np

# Настройка страницы
st.set_page_config(
    page_title="Калькулятор в топ-10 на Wildberries",
    page_icon="📊",
    layout="centered"
)

# Стили для заголовков и кнопок
st.markdown("""
<style>
    .title {
        font-size: 28px;
        font-weight: bold;
        color: #ffffff;
        text-align: center;
        background: linear-gradient(90deg, #6a11cb 0%, #2575fc 100%);
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .subtitle {
        font-size: 16px;
        color: #666666;
        text-align: center;
        margin-bottom: 30px;
    }
    .step {
        font-size: 18px;
        font-weight: bold;
        color: #333333;
        margin-top: 30px;
        margin-bottom: 10px;
    }
    .result-box {
        background-color: #f0f8ff;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #2575fc;
        margin: 20px 0;
    }
    .budget-box {
        background-color: #fff8e1;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #ffc107;
        margin: 20px 0;
    }
</style>
""", unsafe_allow_html=True)

# Заголовок
st.markdown('<div class="title">Калькулятор в топ-10 на Wildberries</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Автоматизированный расчет раздачи для поднятия позиций</div>', unsafe_allow_html=True)

# Инициализация состояния
if 'file_uploaded' not in st.session_state:
    st.session_state.file_uploaded = False
if 'best_query' not in st.session_state:
    st.session_state.best_query = None
if 'target_sales' not in st.session_state:
    st.session_state.target_sales = 0
if 'days' not in st.session_state:
    st.session_state.days = 0
if 'calculated' not in st.session_state:
    st.session_state.calculated = False

# Шаг 1: Ввод данных
st.markdown('<div class="step">1. Ввод данных</div>', unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "Загрузите файл отчета «Сравнение карточек» (Excel)",
    type=["xlsx"],
    help="Файл должен содержать вкладки с данными по запросам и показателям."
)

if uploaded_file is not None:
    st.session_state.file_uploaded = True

# Кнопка рассчитать
if st.button("Рассчитать", key="calculate_btn", use_container_width=True):
    if not uploaded_file:
        st.error("Пожалуйста, загрузите файл с данными.")
    else:
        try:
            # Загрузка файла
            df_queries = pd.read_excel(uploaded_file, sheet_name="Поисковые запросы по всем артикулам")
            df_metrics = pd.read_excel(uploaded_file, sheet_name="Показатели")

            # Фильтрация данных: оставляем только строки с заказами
            df_queries = df_queries[df_queries['Заказы'] > 0].copy()

            # Проверяем наличие нужных столбцов
            required_cols = ['Поисковый запрос', 'Количество запросов', 'Конверсия в корзину из поиска', 'Конверсия в заказ из поиска']
            if not all(col in df_queries.columns for col in required_cols):
                st.error("В файле отсутствуют необходимые столбцы. Убедитесь, что файл содержит: Поисковый запрос, Количество запросов, Конверсия в корзину из поиска, Конверсия в заказ из поиска.")
            else:
                # Вычисляем оценку для каждого запроса: K * CR1 * CR2 * R
                # Для R используем среднее значение по артикулу (если есть) или усредненное значение
                # Предположим, что в таблице "Показатели" есть строка с общими метриками
                if 'Процент выкупа' in df_metrics.columns:
                    avg_r = df_metrics['Процент выкупа'].mean() / 100  # Переводим в долю
                else:
                    avg_r = 0.46  # Значение по умолчанию

                # Добавляем колонку с оценкой
                df_queries['Оценка'] = (
                    df_queries['Количество запросов'] *
                    (df_queries['Конверсия в корзину из поиска'] / 100) *
                    (df_queries['Конверсия в заказ из поиска'] / 100) *
                    avg_r
                )

                # Находим лучший запрос
                best_row = df_queries.loc[df_queries['Оценка'].idxmax()]
                best_query = best_row['Поисковый запрос']
                k = best_row['Количество запросов']

                # Целевые выкупы: 90 за 14 дней, но для быстрого эффекта берем 10 дней
                target_sales = 90
                days = 10

                # Сохраняем результаты в состояние
                st.session_state.best_query = best_query
                st.session_state.target_sales = target_sales
                st.session_state.days = days
                st.session_state.calculated = True

                st.success("✅ Расчет завершен! Перейдите к следующему шагу.")

        except Exception as e:
            st.error(f"Ошибка при обработке файла: {str(e)}")

# Шаг 2: Результат
if st.session_state.calculated:
    st.markdown('<div class="step">2. Результат</div>', unsafe_allow_html=True)

    st.markdown('<div class="result-box">', unsafe_allow_html=True)
    st.write(f"**Самый конверсионный запрос:** {st.session_state.best_query}")
    st.write(f"**Целевое количество выкупов:** {st.session_state.target_sales}")
    st.write(f"**Рекомендуемый срок раздачи:** {st.session_state.days} дней")
    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("Рассчитать бюджет", key="budget_btn", use_container_width=True):
        st.session_state.show_budget_input = True

# Шаг 3: Бюджет
if hasattr(st.session_state, 'show_budget_input') and st.session_state.show_budget_input:
    st.markdown('<div class="step">3. Бюджет</div>', unsafe_allow_html=True)

    st.markdown('<div class="budget-box">', unsafe_allow_html=True)
    st.write("Введите финансовые параметры для расчета бюджета:")

    # Ввод данных
    price_spp = st.number_input("Цена товара после СПП (₽)", min_value=0.0, value=1234.0, step=1.0)
    cashback_percent = st.number_input("Размер кэшбэка (%)", min_value=0.0, max_value=100.0, value=60.0, step=1.0)
    cost_price = st.number_input("Себестоимость товара (₽)", min_value=0.0, value=550.0, step=1.0)
    commission_percent = st.number_input("Комиссия WB (%)", min_value=0.0, max_value=100.0, value=34.5, step=0.1)
    logistics = st.number_input("Логистика на 1 ед. (₽)", min_value=0.0, value=107.0, step=1.0)
    tax_percent = st.number_input("Налог (%)", min_value=0.0, max_value=100.0, value=7.0, step=0.1)

    if st.button("Рассчитать общий бюджет", key="final_calculate_btn", use_container_width=True):
        # Расчет бюджета
        target_sales = st.session_state.target_sales

        # Комиссия
        commission = price_spp * (commission_percent / 100)
        # Кэшбэк
        cashback = price_spp * (cashback_percent / 100)
        # Валовая прибыль до налога
        gross_profit = price_spp - commission - logistics - cost_price
        # Налог
        tax = max(0, gross_profit) * (tax_percent / 100)
        # Чистая прибыль (на самом деле убыток)
        net_profit = gross_profit - tax
        # Чистый расход на один выкуп
        net_cost_per_sale = price_spp + cashback + commission + logistics + cost_price + tax - price_spp
        # Общий бюджет
        total_budget = net_cost_per_sale * target_sales

        # Отображение результата
        st.success(f"✅ **Общий бюджет раздачи: {total_budget:,.2f} ₽**")
        st.write(f"Чистый расход на 1 выкуп: {net_cost_per_sale:,.2f} ₽")
        st.write(f"Целевых выкупов: {target_sales}")

        st.markdown('</div>', unsafe_allow_html=True)
