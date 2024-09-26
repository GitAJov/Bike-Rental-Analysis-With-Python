import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns
import streamlit as st

sns.set_theme(style='dark')

# Fungsi untuk menghitung jumlah penyewaan sepeda berdasarkan musim
def season_df(df):
    season_df = df.groupby(by="season", observed=False).agg({
        "total_users": "sum"
        }).sort_values(by="total_users", ascending=False)

    return season_df

# Fungsi untuk menghitung jumlah pengguna umum dan pengguna terdaftar pada hari kerja dan libur berdasarkan cuaca
def range_weather_casual_registered_df(df):
    working_day_df = df[df["working_day"] == "Yes"]
    holiday_df = df[df["working_day"] == "No"]

    weather_working_day_total = working_day_df.groupby("weather", observed=False)["total_users"].sum().reset_index()
    weather_holiday_total = holiday_df.groupby("weather", observed=False)["total_users"].sum().reset_index()

    weather_working_day_total["Day Type"] = "Working Day"
    weather_holiday_total["Day Type"] = "Holiday"

    combined_df = pd.concat([weather_working_day_total, weather_holiday_total]).sort_values(by="total_users", ascending=False)
    return combined_df

# Fungsi untuk menghitung jumlah penyewaan sepeda berdasarkan hari
def range_day_casual_registered_df(df):
    weekday_grouped_df = df.groupby(by="weekday", observed=False).agg({
        "casual": "sum",
        "registered": "sum",
        "total_users": "sum"
    }).reset_index()

    weekday_grouped_df['weekday'] = weekday_grouped_df['weekday'].replace([0, 1, 2, 3, 4, 5, 6], ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'])
    return weekday_grouped_df

# Fungsi untuk mengolah waktu menjadi label-label tertentu.
def time_label(hour):
    if 5 <= hour < 7 or 9 <= hour < 12:
        return "Morning"
    elif 7 <= hour < 9:
        return "Morning Rush"
    elif 12 <= hour < 15:
        return "Afternoon"
    elif 15 <= hour < 17:
        return "Evening"
    elif 17 <= hour < 19:
        return "Evening Rush"
    else:
        return "Night"
    
# Fungsi untuk menghitung jumlah penyewaan sepeda berdasarkan label waktu
def time_label_grouped_df(df):
    df["time_label"] = df["hour"].apply(lambda x: time_label(x))

    time_label_grouped_df = df.groupby("time_label").agg({
        "total_users": "sum"
    }).sort_values(by="total_users", ascending=False).reset_index()

    return time_label_grouped_df

# Fungsi untuk menghitung jumlah penyewaan sepeda berdasarkan rentang suhu
def temperature_bin_df(df):
    df["temperature_real"] = df["temperature"] * 41

    temperature_bins = pd.cut(df["temperature_real"], bins=5, precision=1)

    temperature_bins = temperature_bins.apply(lambda x: f"{x.left:.1f}-{x.right:.1f}")
    df["temperature_bins"] = temperature_bins

    temperature_bin_df = df.groupby("temperature_bins", observed=False).agg({
        "total_users": "sum"
    }).reset_index()

    return temperature_bin_df

# Pemuatan data
day_df = pd.read_csv("main_day_df.csv")
hour_df = pd.read_csv("main_hour_df.csv")

# Konversi kolom date menjadi tipe data datetime
day_df["date"] = pd.to_datetime(day_df["date"])
hour_df["date"] = pd.to_datetime(hour_df["date"])

# Menentukan minimal dan maksimal rentang tanggal yang dapat dipilih
min_date = day_df["date"].min().date()
max_date = day_df["date"].max().date()

# Sidebar
with st.sidebar:
    st.image("https://plus.unsplash.com/premium_photo-1682125270920-39b89bb20867?q=80&w=2080&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D")
    
    start_date, end_date = st.date_input(
        label='Time Range',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

# Filter data berdasarkan rentang tanggal
main_day_df = day_df[(day_df["date"] >= pd.to_datetime(start_date)) & 
                (day_df["date"] <= pd.to_datetime(end_date))]

main_hour_df = hour_df[(hour_df["date"] >= pd.to_datetime(start_date)) &
                (hour_df["date"] <= pd.to_datetime(end_date))]

# Bagian utama
st.header("Bike Rentals Dashboard :bike:")

# Menampilkan total penyewaan sepeda, pengguna umum, dan pengguna terdaftar pada rentang tanggal yang dipilih
st.subheader("Total Bike Rentals")

col1, col2, col3 = st.columns(3)

with col1:
    total_users = main_day_df["total_users"].sum()
    st.metric("Total Users", total_users)    

with col2:
    total_casual = main_day_df["casual"].sum()
    st.metric("Total Casual", total_casual)

with col3:
    total_registered = main_day_df["registered"].sum()
    st.metric("Total Registered", total_registered)

# Menampilkan grafik  berupa bar chart yang menunjukkan jumlah penyewaan sepeda per hari selama rentang tanggal yang dipilih
fig, ax = plt.subplots(figsize=(16, 8))

ax.plot(main_day_df["date"], main_day_df["total_users"], marker='o', linewidth=2, color="#90CAF9")

ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
 
st.pyplot(fig)

# Menampilkan grafik berupa bar chart yang menunjukkan jumlah penyewaan sepeda berdasarkan musim.
st.subheader("Best Season for Bike Rentals")

season_day_df = season_df(day_df)

fig, ax = plt.subplots(figsize=(10, 5))
sns.barplot(y="season", x="total_users", hue="season", data=season_day_df, palette=["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3"],  ax=ax)

ax.set_xlabel(None)
ax.set_xticklabels(ax.get_xticks(), rotation=45)
ax.xaxis.set_major_formatter(ticker.StrMethodFormatter('{x:,.0f}'))
ax.set_ylabel(None)
st.pyplot(fig)

# Menampilkan grafik berupa bar chart yang menunjukkan jumlah penyewaan sepeda berdasarkan cuaca.
st.subheader("Best Weather for Bike Rentals on Working Days and Holidays")

combined_df = range_weather_casual_registered_df(main_hour_df)

fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(x='weather', y='total_users', hue='Day Type', data=combined_df, palette="Blues", ax=ax)
ax.set_title('Number of Bike Rentals on Working Days and Holidays by Weather')
ax.set_xlabel(None)
ax.set_ylabel(None)
ax.set_xticks([0, 1, 2, 3])
ax.set_xticklabels(['Clear', 'Mist', 'Light Rain/Snow', 'Heavy Rain/Snow'])   
ax.yaxis.set_major_formatter(ticker.StrMethodFormatter('{x:,.0f}'))
st.pyplot(fig)

# Menampilkan grafik berupa line plot yang menunjukkan jumlah penyewaan sepeda berdasarkan hari 
st.subheader("Bike Rentals Based on Day (Casual and Registered)")
weekday_grouped_df = range_day_casual_registered_df(main_day_df)
col1, col2 = st.columns(2)

with col1:
    best_day_casual = weekday_grouped_df["casual"].idxmax()
    st.metric("Best Day", weekday_grouped_df.loc[best_day_casual, "weekday"])  

with col2:
    best_day_registered = weekday_grouped_df["registered"].idxmax()
    st.metric("Best Day", weekday_grouped_df.loc[best_day_registered, "weekday"])

fig, ax = plt.subplots(1, 2, figsize=(15, 6))
sns.lineplot(data=weekday_grouped_df, x='weekday', y='casual', marker='o', ax=ax[0])
ax[0].set_title('Number of Bike Rentals per Day (Casual Users)')
ax[0].set_xlabel(None)
ax[0].set_ylabel(None)
ax[0].set_ylim(0, weekday_grouped_df['total_users'].max()+1)
ax[0].yaxis.set_major_formatter(ticker.StrMethodFormatter('{x:,.0f}'))

sns.lineplot(data=weekday_grouped_df, x='weekday', y='registered', marker='o', ax=ax[1])
ax[1].set_title('Number of Bike Rentals per Day (Registered Users)')
ax[1].set_xlabel(None)
ax[1].set_ylabel(None)
ax[1].set_ylim(0, weekday_grouped_df['total_users'].max())
ax[1].yaxis.set_major_formatter(ticker.StrMethodFormatter('{x:,.0f}'))
st.pyplot(fig)

# Menampilkan grafik jumlah penyewaan sepeda berdasarkan label waktu menggunakan Manual Grouping
st.subheader("Busiest Time for Bike Rentals")

time_label_grouped_df = time_label_grouped_df(main_hour_df)
fig, ax = plt.subplots(figsize=(10, 5))

sns.barplot(x="time_label", y="total_users", hue="time_label", data=time_label_grouped_df, palette=["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3",  "#D3D3D3"], ax=ax)

ax.yaxis.set_major_formatter(ticker.StrMethodFormatter('{x:,.0f}'))
ax.set_title("Number of Bike Rentals per Time Label")
ax.set_xlabel(None)
ax.set_ylabel(None)

st.pyplot(fig)

# Menampilkan grafik jumlah penyewaan sepeda berdasarkan rentang suhu menggunakan Binning
st.subheader("Bike Rentals Based on Temperature Range (°C)")
temperature_bin_df = temperature_bin_df(main_hour_df)

fig, ax = plt.subplots(figsize=(10, 5))
sns.barplot(y="temperature_bins", x="total_users", hue="temperature_bins", data=temperature_bin_df, palette=["#90CAF9"], ax=ax)

ax.xaxis.set_major_formatter(ticker.StrMethodFormatter('{x:,.0f}'))
ax.set_title("Number of Bike Rentals per Temperature Range (°C)")
ax.set_xlabel(None)
ax.set_ylabel(None)
ax.set_xticklabels(ax.get_xticks(), rotation=45)

st.pyplot(fig)