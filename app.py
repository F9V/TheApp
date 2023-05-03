import pandas as pd

import glob

import os

import numpy as np

import base64

import matplotlib.pyplot as plt
import streamlit as st


import folium

from streamlit_folium import folium_static
from folium.plugins import MarkerCluster


# a_file_sp ='F:\ScriptIndeed\spon_ads.csv'
# a_file_org ='F:\ScriptIndeed\org_ads.csv'
# a_file_ex ='F:\ScriptIndeed\export.csv'
# a_file_sp_campaign ='F:\ScriptIndeed\spon_camp.csv'

# def ReadAll(file_sp, file_org, file_ex, file_sp_campaign):
def ReadAll(file_sp, file_org, file_ex, file_sp_campaign):
    # Legge files




    spon_annunci = pd.read_csv(file_sp, index_col=None, header = 0,encoding='utf8')



    org_annunci = pd.read_csv(file_org, index_col=None, header = 0,encoding='utf8')


    export = pd.read_csv(file_ex, index_col=None, header = 0,encoding='utf8')



    spon_camp = pd.read_csv(file_sp_campaign, index_col=None, header = 0,encoding='utf8')




    org_annunci['jobReferenceNumber'] = org_annunci['jobReferenceNumber'].fillna('id non assegnato')



    spon_annunci['jobReferenceNumber'] = spon_annunci['jobReferenceNumber'].fillna('id non assegnato')



    spon_annunci.loc[spon_annunci['jobReferenceNumber'].isnull(), 'jobReferenceNumber'] = 'id non assegnato'



    org_annunci.loc[org_annunci['jobReferenceNumber'].isnull(), 'jobReferenceNumber'] = 'id non assegnato'



    spon_annunci_id_non_assegnato = spon_annunci[spon_annunci['jobReferenceNumber'] == 'id non assegnato']


    org_annunci_id_non_assegnato = org_annunci[org_annunci['jobReferenceNumber'] == 'id non assegnato']




    spon_annunci_id_non_assegnato = spon_annunci_id_non_assegnato.groupby('jobReferenceNumber', as_index=False).agg(lambda x: x.sum() if x.name in ['sumImpressions', 'sumClicks', 'sumApplyStarts'] else np.nan)




    org_annunci_id_non_assegnato = org_annunci_id_non_assegnato.groupby('jobReferenceNumber', as_index=False).agg(lambda x: x.sum() if x.name in ['sumImpressions', 'sumClicks', 'sumApplyStarts'] else np.nan)



    spon_annunci = spon_annunci.drop(spon_annunci[spon_annunci['jobReferenceNumber'] == 'id non assegnato'].index)



    org_annunci = org_annunci.drop(org_annunci[org_annunci['jobReferenceNumber'] == 'id non assegnato'].index)



    spon_annunci = pd.concat([spon_annunci, spon_annunci_id_non_assegnato], axis=0)


    org_annunci = pd.concat([org_annunci, org_annunci_id_non_assegnato], axis=0)



    spon_annunci = spon_annunci.rename(columns={"sumApplyStarts": "sponsored apply starts", 'sumClicks': 'sponsored clicks', 'sumImpressions': 'sponsored impressions'})


    org_annunci = org_annunci.rename(columns={"sumApplyStarts": "organic apply starts",'sumClicks': 'organic clicks', 'sumImpressions': 'organic impressions'})



    spon_annunci = spon_annunci[['title','countryFullName','regionFullName','city','sponsored impressions','sponsored clicks','sponsored apply starts','sumCostLocal','jobReferenceNumber',]]




    org_annunci = org_annunci[['title','countryFullName','regionFullName','city','organic impressions','organic clicks','organic apply starts','sumCostLocal','jobReferenceNumber']]









    spon_annunci.fillna(value = 0, inplace = True)
    org_annunci.fillna(value = 0, inplace = True)



    # rimuovi i duplicati dalla colonna 'jobReferenceNumber' e raggruppa i dati nelle altre colonne
    spon_annunci = spon_annunci.groupby('jobReferenceNumber', as_index=False).first()
    org_annunci = org_annunci.groupby('jobReferenceNumber', as_index=False).first()




    tot2 = pd.merge(spon_annunci, org_annunci, on='jobReferenceNumber', how='outer')




    tot2.info()




    tot2['title'] = tot2['title_x'].combine_first(tot2['title_y'])
    tot2.drop(['title_x', 'title_y'], axis=1, inplace=True)



    tot2['countryFullName'] = tot2['countryFullName_x'].combine_first(tot2['countryFullName_y'])
    tot2.drop(['countryFullName_x', 'countryFullName_y'], axis=1, inplace=True)



    tot2['city'] = tot2['city_x'].combine_first(tot2['city_y'])
    tot2.drop(['city_x', 'city_y'], axis=1, inplace=True)




    tot2['regionFullName'] = tot2['regionFullName_x'].combine_first(tot2['regionFullName_y'])
    tot2.drop(['regionFullName_x', 'regionFullName_y'], axis=1, inplace=True)



    tot2.drop(['sumCostLocal_y'], axis=1, inplace=True)



    tot2 = tot2.rename(columns={'sumCostLocal_x': 'budget'})


    # Rinomino colonne reference number e total cost in Export


    export = export.rename(columns={"Reference Number": "jobReferenceNumber", 'Total Cost':'sumCostLocal'})


    # Tengo solo Campaign JobReference Category e sum Cost local di Export


    export= export[['Campaign','jobReferenceNumber','Category','sumCostLocal']]



    # Aggiungiamo una colonna "maxCampaign" per tenere traccia della campagna con il costo massimo
    export['maxCampaign'] = export['Campaign']




    # Raggruppiamo per jobReferenceNumber e sommiamo i costi locali
    grouped_export = export.groupby('jobReferenceNumber').agg({'sumCostLocal': 'sum', 'maxCampaign': 'max', 'Category': 'max'})


    # Selezioniamo soltanto le colonne che ci interessano e rinominiamo "maxCampaign" in "Campaign"
    c = grouped_export[['maxCampaign', 'sumCostLocal', 'Category']].rename(columns={'maxCampaign': 'Campaign'})



    tot_and_campaign = tot2.merge(c, on='jobReferenceNumber', how='outer')




    tot_and_campaign['Category'].fillna(value = '', inplace = True)





    category_split = tot_and_campaign['Category'].str.split('|', expand=True)



    # Rinomina le colonne usando una numerazione sequenziale
    category_split = category_split.rename(columns=lambda x: f"Category{x+1}")


    # Combina i risultati con il dataframe originale
    tot_and_campaign = pd.concat([tot_and_campaign, category_split], axis=1)




    # Rimuove la colonna "Category" originale
    tot_and_campaign.drop('Category', axis=1, inplace=True)



    # Dividi la colonna "Category" in più colonne
    category_split = tot_and_campaign['Category3'].str.split(',', expand=True)



    # Rinomina le colonne usando una numerazione sequenziale
    category_split = category_split.rename(columns=lambda y: f"CategoryD{y+1}")



    # Combina i risultati con il dataframe originale
    tot_and_campaign = pd.concat([tot_and_campaign, category_split], axis=1)


    # Rimuove la colonna "Category" originale
    tot_and_campaign.drop('Category3', axis=1, inplace=True)
    tot_and_campaign.drop('CategoryD4', axis=1, inplace=True)




    tot_and_campaign = tot_and_campaign.rename(columns={"Category1": "Settore", 'Category2': 'Ruolo', 'CategoryD1': 'Funzione Aziendale', 'CategoryD2': 'Esperienza', 'CategoryD3': 'Filiale'})



    spon_camp.rename( columns={'Candidature avviate':'Candidature avviate sponsorizzate','Apply starts':'Candidature avviate sponsorizzate','Campagna':'Campaign'}, inplace=True )






    #inizia la Pivot per le campagne
    #Da spon_camp prendo le candidature sponsorizzate per campagna
    spon_camp = spon_camp.groupby('Campaign')['Candidature avviate sponsorizzate'].sum().reset_index()



    spon_camp.rename( columns={'Campagna':'Campaign'}, inplace=True )


    #Prendo il numero degli annunci da export
    annunci = export.groupby('Campaign')['jobReferenceNumber'].count().reset_index()

    #Prendo il budget da export
    budget = export.groupby('Campaign')['sumCostLocal'].sum().reset_index()



    #Annunci e export insieme
    df2 =  annunci.merge(budget, on=['Campaign'])



    df2.rename( columns={'jobReferenceNumber':'Annunci','sumCostLocal':'Budget'}, inplace=True )





    #crea un nuovo DF da df2 e aggiungo le sponsorizzate da spon_camp
    df3_per_campaign =  df2.merge(spon_camp, on=['Campaign'], how = 'outer')




    #pivot tot_and_campaign to gain organic data per campaign
    tot_and_campaign['Campaign'].fillna(value = "Annunci non in una campagna", inplace = True)


    organic_per_campaign = tot_and_campaign.groupby('Campaign')['organic apply starts'].sum().reset_index()







    #creation of final paronamica
    panoramica = organic_per_campaign.merge(df3_per_campaign, on=['Campaign'], how = 'outer')




    panoramica = panoramica.rename(columns={"organic apply starts": "candidature avviate organiche"})



    panoramica['Candidature avviate organiche per annuncio']= round(panoramica['candidature avviate organiche']/panoramica['Annunci'],1)



    panoramica['Candidature avviate sponsorizzate per annuncio']= round(panoramica['Candidature avviate sponsorizzate']/panoramica['Annunci'],1)



    panoramica['Budget per annuncio']= round(panoramica['Budget']/panoramica['Annunci'],2)



    Ruolo = pd.pivot_table(tot_and_campaign, 
                            index='Ruolo', 
                            values=['budget', 'organic apply starts', 'sponsored apply starts', 'jobReferenceNumber'], 
                            aggfunc={'budget': 'sum', 'organic apply starts': 'sum', 'sponsored apply starts': 'sum', 'jobReferenceNumber': 'count'})


    Ruolo = Ruolo.rename(columns={"budget": "Budget", 'jobReferenceNumber':'Annunci','organic apply starts':'Candidature avviate organiche','sponsored apply starts':'Candidature avviate sponsorizzate'})

    Ruolo['Candidature avviate organiche per annuncio']= round(Ruolo['Candidature avviate organiche']/Ruolo['Annunci'],1)


    Ruolo['Candidature avviate sponsorizzate per annuncio']= round(Ruolo['Candidature avviate sponsorizzate']/Ruolo['Annunci'],1)




    Ruolo['Budget per annuncio']= round(Ruolo['Budget']/Ruolo['Annunci'],2)




    Esperienza = pd.pivot_table(tot_and_campaign, 
                            index='Esperienza', 
                            values=['budget', 'organic apply starts', 'sponsored apply starts', 'jobReferenceNumber'], 
                            aggfunc={'budget': 'sum', 'organic apply starts': 'sum', 'sponsored apply starts': 'sum', 'jobReferenceNumber': 'count'})



    Esperienza = Esperienza.rename(columns={"budget": "Budget", 'jobReferenceNumber':'Annunci','organic apply starts':'Candidature avviate organiche','sponsored apply starts':'Candidature avviate sponsorizzate'})




    Esperienza['Candidature avviate organiche per annuncio']= round(Esperienza['Candidature avviate organiche']/Esperienza['Annunci'],1)




    Esperienza['Candidature avviate sponsorizzate per annuncio']= round(Esperienza['Candidature avviate sponsorizzate']/Esperienza['Annunci'],1)




    Esperienza['Budget per annuncio']= round(Esperienza['Budget']/Esperienza['Annunci'],2)




    Settore = pd.pivot_table(tot_and_campaign, 
                            index='Settore', 
                            values=['budget', 'organic apply starts', 'sponsored apply starts', 'jobReferenceNumber'], 
                            aggfunc={'budget': 'sum', 'organic apply starts': 'sum', 'sponsored apply starts': 'sum', 'jobReferenceNumber': 'count'})




    Settore = Settore.rename(columns={"budget": "Budget", 'jobReferenceNumber':'Annunci','organic apply starts':'Candidature avviate organiche','sponsored apply starts':'Candidature avviate sponsorizzate'})



    Settore['Candidature avviate organiche per annuncio']= round(Settore['Candidature avviate organiche']/Settore['Annunci'],1)



    Settore['Candidature avviate sponsorizzate per annuncio']= round(Settore['Candidature avviate sponsorizzate']/Settore['Annunci'],1)



    Settore['Budget per annuncio']= round(Settore['Budget']/Settore['Annunci'],2)




    Filiale = pd.pivot_table(tot_and_campaign, 
                            index='Filiale', 
                            values=['budget', 'organic apply starts', 'sponsored apply starts', 'jobReferenceNumber'], 
                            aggfunc={'budget': 'sum', 'organic apply starts': 'sum', 'sponsored apply starts': 'sum', 'jobReferenceNumber': 'count'})



    Filiale = Filiale.rename(columns={"budget": "Budget", 'jobReferenceNumber':'Annunci','organic apply starts':'Candidature avviate organiche','sponsored apply starts':'Candidature avviate sponsorizzate'})


    Filiale['Candidature avviate organiche per annuncio']= round(Filiale['Candidature avviate organiche']/Filiale['Annunci'],1)




    Filiale['Candidature avviate sponsorizzate per annuncio']= round(Filiale['Candidature avviate sponsorizzate']/Filiale['Annunci'],1)




    Filiale['Budget per annuncio']= round(Filiale['Budget']/Filiale['Annunci'],2)


    Funzione_Aziendale = pd.pivot_table(tot_and_campaign, 
                            index='Funzione Aziendale', 
                            values=['budget', 'organic apply starts', 'sponsored apply starts', 'jobReferenceNumber'], 
                            aggfunc={'budget': 'sum', 'organic apply starts': 'sum', 'sponsored apply starts': 'sum', 'jobReferenceNumber': 'count'})



    Funzione_Aziendale = Funzione_Aziendale.rename(columns={"budget": "Budget", 'jobReferenceNumber':'Annunci','organic apply starts':'Candidature avviate organiche','sponsored apply starts':'Candidature avviate sponsorizzate'})


    Funzione_Aziendale['Candidature avviate organiche per annuncio']= round(Funzione_Aziendale['Candidature avviate organiche']/Funzione_Aziendale['Annunci'],1)




    Funzione_Aziendale['Candidature avviate sponsorizzate per annuncio']= round(Funzione_Aziendale['Candidature avviate sponsorizzate']/Funzione_Aziendale['Annunci'],1)




    Funzione_Aziendale['Budget per annuncio']= round(Funzione_Aziendale['Budget']/Funzione_Aziendale['Annunci'],2)




    Generale = pd.DataFrame({'budget': [tot_and_campaign['budget'].sum()],
                            'organic apply starts': [tot_and_campaign['organic apply starts'].sum()],
                            'sponsored apply starts': [tot_and_campaign['sponsored apply starts'].sum()],
                            'jobReferenceNumber': [tot_and_campaign['jobReferenceNumber'].count()]})



    Generale = Generale.rename(columns={"budget": "Budget", 'jobReferenceNumber':'Annunci','organic apply starts':'Candidature avviate organiche','sponsored apply starts':'Candidature avviate sponsorizzate'})




    Generale['Candidature avviate organiche per annuncio']= round(Generale['Candidature avviate organiche']/Generale['Annunci'],1)




    Generale['Candidature avviate sponsorizzate per annuncio']= round(Generale['Candidature avviate sponsorizzate']/Generale['Annunci'],1)



    Generale['Budget per annuncio']= round(Generale['Budget']/Generale['Annunci'],2)


    Ruolo= Ruolo.reset_index()
    Esperienza= Esperienza.reset_index()
    Settore= Settore.reset_index()
    Filiale= Filiale.reset_index()
    Funzione_Aziendale= Funzione_Aziendale.reset_index()
    
    tot3 = tot_and_campaign.drop(columns= 'Campaign')

    # Visualizziamo il risultato result.to_excel("panoramica.xlsx")

    return tot3, panoramica, Ruolo, Settore, Filiale, Esperienza, Generale, Funzione_Aziendale



def convert_df_to_csv(df):
  # IMPORTANT: Cache the conversion to prevent computation on every rerun
  return df.to_csv().encode('utf-8')

def convert_df(df):
   
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    return b64









def crea_mappa():
    # data_italy = pd.read_excel("/Users/bbuttiglione/Desktop/untitled_folder/citta_ita.xlsx")
    script_dir = os.path.abspath( os.path.dirname( __file__ ) )

    os.chdir(script_dir)
    data_italy = pd.read_csv("italy_geo.csv", encoding="utf-8")




    mappa_citta = pd.merge(g_tot_and_campaign, data_italy[['city', 'lat', 'lon']], on='city', how='left')

    # Elimina le righe in cui il campo "city" è nullo
    mappa_citta = mappa_citta.dropna(subset=['lat'])
    mappa_citta = mappa_citta.dropna(subset=['lon'])
    mappa_citta['ann']= 1
    mappa_citta['budget_per_ad']= 0









    mappa_citta["lat"] = mappa_citta["lat"].astype("float")



    # Lista delle metriche
    metriche = ["sumCostLocal", "organic apply starts","sponsored apply starts","budget_per_ad","apply starts spons per ad","apply starts org per ad","costo per apply start spons"]


    # Lista dei ruoli
    ruoli = list(mappa_citta["Ruolo"].unique())

    esperienza = list(mappa_citta["Esperienza"].unique())

    settore = list(mappa_citta["Settore"].unique())

    filiale = list(mappa_citta["Filiale"].unique())

    funzione_aziendale = list(mappa_citta["Funzione Aziendale"].unique())

    # Funzione per filtrare il dataframe in base alle selezioni di campagne e ruoli
    def filtra_dataframe(df, ruoli_sel,esperienza_sel,settore_sel,filiale_sel,funzione_aziendale_sel):
        df_filtrato = df.copy()
        if ruoli_sel:
            df_filtrato = df_filtrato[df_filtrato["Ruolo"].isin(ruoli_sel)]

        if esperienza_sel:
            df_filtrato = df_filtrato[df_filtrato["Esperienza"].isin(esperienza_sel)]

        if settore_sel:
            df_filtrato = df_filtrato[df_filtrato["Settore"].isin(settore_sel)]


        if filiale_sel:
            df_filtrato = df_filtrato[df_filtrato["Filiale"].isin(filiale_sel)]

        if funzione_aziendale_sel:
            df_filtrato = df_filtrato[df_filtrato["Funzione Aziendale"].isin(funzione_aziendale_sel)]

        

        
        return df_filtrato



    def calcola_metriche(df_filtrato, metriche_selezionate, valore_slider):

        if metriche_selezionate == 'budget_per_ad':
            df_agg = df_filtrato.groupby('city').agg({'sumCostLocal': 'sum', 'ann': 'sum'})
            df_agg['budget_per_ad'] = df_agg['sumCostLocal']/df_agg['ann']
            df_agg.drop(columns=['sumCostLocal','ann'])
            # df_agg = df_agg[df_agg['budget_per_ad'] >= valore_slider]

            
            df_agg = df_agg[df_agg["budget_per_ad"] >= valore_slider[0]]
            df_agg = df_agg[df_agg["budget_per_ad"] <= valore_slider[1]]


            df_agg = pd.merge(df_agg, mappa_citta[["city", "lat", "lon"]], on="city")


        elif metriche_selezionate == 'apply starts spons per ad':

            df_agg = df_filtrato.groupby('city').agg({'sponsored apply starts': 'sum', 'ann': 'sum'})
            df_agg['apply starts spons per ad'] = df_agg['sponsored apply starts']/df_agg['ann']
            df_agg.drop(columns=['sponsored apply starts','ann'])
            # df_agg = df_agg[df_agg['apply starts spons per ad'] >= valore_slider]

            
            df_agg = df_agg[df_agg["apply starts spons per ad"] >= valore_slider[0]]
            df_agg = df_agg[df_agg["apply starts spons per ad"] <= valore_slider[1]]


            df_agg = pd.merge(df_agg, mappa_citta[["city", "lat", "lon"]], on="city")


        elif metriche_selezionate == 'apply starts org per ad':

            df_agg = df_filtrato.groupby('city').agg({'organic apply starts': 'sum', 'ann': 'sum'})
            df_agg['apply starts org per ad'] = df_agg['organic apply starts']/df_agg['ann']
            df_agg.drop(columns=['organic apply starts','ann'])
            # df_agg = df_agg[df_agg['apply starts org per ad'] >= valore_slider]


            df_agg = df_agg[df_agg["apply starts org per ad"] >= valore_slider[0]]
            df_agg = df_agg[df_agg["apply starts org per ad"] <= valore_slider[1]]

            df_agg = pd.merge(df_agg, mappa_citta[["city", "lat", "lon"]], on="city")


        elif metriche_selezionate == 'costo per apply start spons':

            df_agg = df_filtrato.groupby('city').agg({'sumCostLocal': 'sum', 'sponsored apply starts': 'sum'})


            df_agg['costo per apply start spons'] = np.where(df_agg['sponsored apply starts'] != 0, 
                                                     df_agg['sumCostLocal'] / df_agg['sponsored apply starts'], 
                                                     np.nan)

            # df_agg = df_agg[df_agg['costo per apply start spons'] >= valore_slider]


            df_agg = df_agg[df_agg["costo per apply start spons"] >= valore_slider[0]]
            df_agg = df_agg[df_agg["costo per apply start spons"] <= valore_slider[1]]

            df_agg = pd.merge(df_agg, mappa_citta[["city", "lat", "lon"]], on="city")


           
                
            

        else:
            df_agg = df_filtrato.groupby("city")[metriche_selezionate].sum().reset_index()
            # df_agg = df_agg[df_agg[metriche_selezionate] >= valore_slider]

            df_agg = df_agg[df_agg[metriche_selezionate] >= valore_slider[0]]
            df_agg = df_agg[df_agg[metriche_selezionate] <= valore_slider[1]]

            df_agg = pd.merge(df_agg, mappa_citta[["city", "lat", "lon"]], on="city")
            
        return df_agg


    

   

    # Interfaccia utente
    st.sidebar.title("Filtro per campagna e ruolo")
    ruoli_sel = st.sidebar.multiselect("Seleziona uno o più ruoli", ruoli, default=ruoli)
    esperienza_sel = st.sidebar.multiselect("Seleziona l'esperienza", esperienza, default=esperienza)
    settore_sel = st.sidebar.multiselect("Seleziona il settore", settore, default=settore)
    filiale_sel = st.sidebar.multiselect("Seleziona la filiale", filiale, default=filiale)
    funzione_aziendale_sel = st.sidebar.multiselect("Seleziona la funzione aziendale", funzione_aziendale, default=funzione_aziendale)

    metriche_selezionate = st.sidebar.selectbox("Seleziona una metrica", metriche, index=0)




    mappa_citta_filtrato = filtra_dataframe(mappa_citta, ruoli_sel,esperienza_sel,settore_sel,filiale_sel,funzione_aziendale_sel)

    if metriche_selezionate == 'budget_per_ad':
        df_agg_max = mappa_citta_filtrato.groupby('city').agg({'sumCostLocal': 'sum', 'ann': 'sum'})
        df_agg_max['budget_per_ad'] = df_agg_max['sumCostLocal']/df_agg_max['ann']
        df_agg_max = df_agg_max['budget_per_ad'].max()

    elif metriche_selezionate == 'apply starts spons per ad':
        df_agg_max = mappa_citta_filtrato.groupby('city').agg({'sponsored apply starts': 'sum', 'ann': 'sum'})
        df_agg_max['apply starts spons per ad'] = df_agg_max['sponsored apply starts']/df_agg_max['ann']
        df_agg_max = df_agg_max['apply starts spons per ad'].max()

    elif metriche_selezionate == 'apply starts org per ad':
        df_agg_max = mappa_citta_filtrato.groupby('city').agg({'organic apply starts': 'sum', 'ann': 'sum'})
        df_agg_max['apply starts org per ad'] = df_agg_max['organic apply starts']/df_agg_max['ann']
        df_agg_max = df_agg_max['apply starts org per ad'].max()

    elif metriche_selezionate == 'costo per apply start spons':
        
        df_agg_max = mappa_citta_filtrato.groupby('city').agg({'sumCostLocal': 'sum', 'sponsored apply starts': 'sum'})


        df_agg_max['costo per apply start spons'] = np.where(df_agg_max['sponsored apply starts'] != 0, 
                                                     df_agg_max['sumCostLocal'] / df_agg_max['sponsored apply starts'], 
                                                     np.nan)

        df_agg_max = df_agg_max['costo per apply start spons'].max()
        


    else:
        df_agg_max = mappa_citta_filtrato.groupby("city")[metriche_selezionate].sum().reset_index()
        df_agg_max = df_agg_max[metriche_selezionate].max()
        


    valore_slider = st.sidebar.slider("Seleziona un valore per la metrica", 0.00, float(df_agg_max), (float(df_agg_max/2),float(df_agg_max)))

    # Filtraggio del dataframe

    # Calcolo della somma delle metriche per ciascuna città
    mappa_citta_agg = calcola_metriche(mappa_citta_filtrato, metriche_selezionate, valore_slider)


    mappa_citta_agg = mappa_citta_agg.drop_duplicates(subset=['city'])

    # Creazione della mappa
    # Crea la mappa e il MarkerCluster
    mappa = folium.Map(location=[42.504154, 12.646361], zoom_start=6)
    marker_cluster = MarkerCluster().add_to(mappa)

    # Aggiungi i marker al MarkerCluster
    for i, row in mappa_citta_agg.iterrows():
        popup_text = f"<b>City:</b> {row['city']}<br>"
        popup_text += f"<b>{metriche_selezionate}:</b> {row[metriche_selezionate]:,.0f}<br>"
        folium.Marker([row["lat"], row["lon"]], popup=popup_text).add_to(marker_cluster)

    # Aggiungi Leaflet.markercluster come plugin alla mappa
    folium.plugins.MarkerCluster().add_to(mappa)
    
    #for i, row in mappa_citta_agg.iterrows():

        
    #    popup_text = f"<b>City:</b> {row['city']}<br>"
    #    popup_text += f"<b>{metriche_selezionate}:</b> {row[metriche_selezionate]:,.0f}<br>"
    #    folium.Marker([row["lat"], row["lon"]], popup=popup_text).add_to(mappa)

    # Visualizzazione della mappa
    

    return folium_static(mappa)




def main_style():
    st.markdown(
    """
    <style>
    [data-baseweb="select"] > div:first-child {
        max-height: 200px !important;
    }
    [data-baseweb="select"] > div:first-child > div:first-child {
        overflow-y:scroll;
    }
    iframe{
        width:100%;
        min-height: 640px;
    }
    [tabindex="0"] > .css-z5fcl4{
        padding: 3rem 4rem 2rem;
    }

    [data-testid="stMarkdownContainer"] > p:first-child {
        font-size:22px;
    }


    </style>
    """,
    unsafe_allow_html=True,
    )

# ---------------------------------------- Fine Funzioni -----------------------------------------------------




# Titolo dell'applicazione
st.set_page_config(page_title="Umanapp - Applicazione di visualizzazione dei dati", page_icon=":chart_with_upwards_trend:",layout="wide")
st.title("Umanapp - Applicazione di visualizzazione dei dati")


# Menu a tab
menu = ["Caricamento file CSV", "Visualizzazione mappa"]
choice = st.sidebar.selectbox("Seleziona un'opzione", menu)

# Carica i file CSV

global df1
global df2
global df3
global df4

df1 = None
df2 = None
df3 = None
df4 = None



global g_tot_and_campaign
global g_panoramica

global g_ruolo
global g_settore
global g_esperienza
global g_filiale
global g_generale


global g_ready_download
g_ready_download = None



g_tot_and_campaign = None
g_panoramica = None



g_ruolo = None
g_settore = None
g_esperienza = None
g_filiale = None
g_generale = None





main_style()


# g_tot_and_campaign, g_panoramica, g_ruolo, g_settore, g_filiale, g_esperienza, g_generale = ReadAll(a_file_sp,a_file_org,a_file_ex,a_file_sp_campaign)
# crea_mappa()
# print(g_tot_and_campaign)



if choice == "Caricamento file CSV":

    

    st.header("Carica i tuoi file CSV")
    uploaded_file_1 = st.file_uploader("Carica il CSV degli annunci sponsorizzati", type=["csv"])
    uploaded_file_2 = st.file_uploader("Carica il CSV degli annunci organici", type=["csv"])
    uploaded_file_3 = st.file_uploader("Carica il CSV della sezione export", type=["csv"])
    uploaded_file_4 = st.file_uploader("Carica il CSV delle campagne sponsorizzate", type=["csv"])

    # Importa i file CSV come DataFrame
    if uploaded_file_1 is not None and uploaded_file_2 is not None and uploaded_file_3 is not None and uploaded_file_4 is not None:
        read_button = st.button("Carica i files") # Give button a variable name
    
        if read_button: # Make button a condition.
            st.text("Caricamento files...")
            g_tot_and_campaign, g_panoramica, g_ruolo, g_settore, g_filiale, g_esperienza, g_generale,g_funzione_aziendale = ReadAll(uploaded_file_1,uploaded_file_2,uploaded_file_3,uploaded_file_4) 
            st.text("Caricamento avvenuto con successo")
            
            st.text("Generando files per il download...")
            
            st.session_state.g_tot_and_campaign = g_tot_and_campaign
            st.session_state.g_panoramica = g_panoramica
            st.session_state.g_ruolo = g_ruolo
            st.session_state.g_settore = g_settore
            st.session_state.g_filiale = g_filiale
            st.session_state.g_esperienza = g_esperienza
            st.session_state.g_generale = g_generale
            st.session_state.g_funzione_aziendale = g_funzione_aziendale
            

            csv_tot_and_campaign = convert_df(g_tot_and_campaign)
            csv_panoramica = convert_df(g_panoramica)

            csv_ruolo = convert_df(g_ruolo)
            csv_settore = convert_df(g_settore)
            csv_filiale = convert_df(g_filiale)
            csv_esperienza = convert_df(g_esperienza)
            csv_generale = convert_df(g_generale)
            csv_g_funzione_aziendale = convert_df(g_funzione_aziendale)

            st.text("Ora puoi scaricare i file con le tabelle:")

            st.markdown(f'<a href="data:file/csv;base64,{csv_tot_and_campaign}" download="Tutti_gli_annunci.csv">Download Tutti_gli_annunci.csv</a>', unsafe_allow_html=True)

            st.markdown(f'<a href="data:file/csv;base64,{csv_panoramica}" download="Panoramica.csv">Download Panoramica.csv</a>', unsafe_allow_html=True)

            
            st.markdown(f'<a href="data:file/csv;base64,{csv_ruolo}" download="Ruolo.csv">Download Ruolo.csv</a>', unsafe_allow_html=True)

            st.markdown(f'<a href="data:file/csv;base64,{csv_settore}" download="Settore.csv">Download Settore.csv</a>', unsafe_allow_html=True)
            
            st.markdown(f'<a href="data:file/csv;base64,{csv_filiale}" download="Filiale.csv">Download Filiale.csv</a>', unsafe_allow_html=True)

            st.markdown(f'<a href="data:file/csv;base64,{csv_esperienza}" download="Esperienza.csv">Download Esperienza.csv</a>', unsafe_allow_html=True)
            
            st.markdown(f'<a href="data:file/csv;base64,{csv_generale}" download="Generale.csv">Download Generale.csv</a>', unsafe_allow_html=True)

            st.markdown(f'<a href="data:file/csv;base64,{csv_g_funzione_aziendale}" download="Funzione Aziendale.csv">Download Funzione Aziendale.csv</a>', unsafe_allow_html=True)

    elif uploaded_file_1 is None or uploaded_file_2 is None or uploaded_file_3 is None or uploaded_file_4 is None:
         if "g_tot_and_campaign" in st.session_state:
            g_tot_and_campaign = st.session_state.g_tot_and_campaign
            g_panoramica = st.session_state.g_panoramica
            g_ruolo = st.session_state.g_ruolo
            g_settore= st.session_state.g_settore
            g_filiale = st.session_state.g_filiale
            g_esperienza = st.session_state.g_esperienza
            g_generale = st.session_state.g_generale

            csv_tot_and_campaign = convert_df(g_tot_and_campaign)
            csv_panoramica = convert_df(g_panoramica)

            csv_ruolo = convert_df(g_ruolo)
            csv_settore = convert_df(g_settore)
            csv_filiale = convert_df(g_filiale)
            csv_esperienza = convert_df(g_esperienza)
            csv_generale = convert_df(g_generale)


            st.text("Ora puoi scaricare i file con le tabelle:")

            st.markdown(f'<a href="data:file/csv;base64,{csv_tot_and_campaign}" download="Tutti_gli_annunci.csv">Download Tutti_gli_annunci.csv</a>', unsafe_allow_html=True)

            st.markdown(f'<a href="data:file/csv;base64,{csv_panoramica}" download="Panoramica.csv">Download Panoramica.csv</a>', unsafe_allow_html=True)

            
            st.markdown(f'<a href="data:file/csv;base64,{csv_ruolo}" download="Ruolo.csv">Download Ruolo.csv</a>', unsafe_allow_html=True)

            st.markdown(f'<a href="data:file/csv;base64,{csv_settore}" download="Settore.csv">Download Settore.csv</a>', unsafe_allow_html=True)
            
            st.markdown(f'<a href="data:file/csv;base64,{csv_filiale}" download="Filiale.csv">Download Filiale.csv</a>', unsafe_allow_html=True)

            st.markdown(f'<a href="data:file/csv;base64,{csv_esperienza}" download="Esperienza.csv">Download Esperienza.csv</a>', unsafe_allow_html=True)
            
            st.markdown(f'<a href="data:file/csv;base64,{csv_generale}" download="Generale.csv">Download Generale.csv</a>', unsafe_allow_html=True)




# Visualizzazioni dei dati
if choice == "Visualizzazione mappa":
    st.header("Visualizzazione mappa")
    
    
    if "g_tot_and_campaign" in st.session_state:
        g_tot_and_campaign = st.session_state.g_tot_and_campaign
        g_panoramica = st.session_state.g_panoramica
        g_ruolo = st.session_state.g_ruolo
        g_settore= st.session_state.g_settore
        g_filiale = st.session_state.g_filiale
        g_esperienza = st.session_state.g_esperienza
        g_generale = st.session_state.g_generale

        crea_mappa()
    elif "g_tot_and_campaign" not in st.session_state:
        st.text("File non trovati.")
        st.text("Assicurati di aver effettuato l'upload dei file nella sezione ''Caricamento CSV''")


