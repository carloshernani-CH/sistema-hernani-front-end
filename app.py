import streamlit as st
import requests
import pandas as pd
from fpdf import FPDF
from io import BytesIO

API_URL = "https://sistema-hernani-back-end.onrender.com"

def clean_data(records):
    for record in records:
        for key, value in record.items():
            if isinstance(value, list):
                record[key] = ', '.join(map(str, value))
            else:
                record[key] = str(value)
    return records

def get_all_patient_names():
    response = requests.get(f"{API_URL}/get_records")
    if response.status_code == 200:
        records = response.json()
        return [record["NOME"] for record in records]
    return []

def get_record_by_name(name):
    response = requests.get(f"{API_URL}/get_records")
    if response.status_code == 200:
        records = response.json()
        for record in records:
            if record["NOME"] == name:
                return record
    return None

def generate_pdf(records):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    for record in records:
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        for key, value in record.items():
            pdf.cell(200, 10, txt=f"{key}: {value}", ln=True)

    pdf_output = pdf.output(dest='S').encode('latin1')
    pdf_bytes = BytesIO(pdf_output)

    return pdf_bytes

def login(username, password):
    response = requests.post(f"{API_URL}/login", json={"username": username, "password": password})
    if response.status_code == 200:
        return True
    else:
        return False

def main():
    st.title("Modelo organizacional")

    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        st.subheader("Login")

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if login(username, password):
                st.success("Login bem-sucedido!")
                st.session_state.logged_in = True
                st.experimental_rerun()  # Recarrega a página para esconder a seção de login
            else:
                st.error("Credenciais inválidas!")
    else:
        option = st.sidebar.selectbox("Selecionar Ação", ["Adicionar Dados", "Ver Dados", "Atualizar Dados", "Deletar Dados", "Logout"])

        if option == "Logout":
            st.session_state.logged_in = False
            st.experimental_rerun()

        if option == "Adicionar Dados":
            st.subheader("Adicionar Dados")
            data = st.date_input("Data")
            data_de_nasc = st.date_input("Data de Nascimento")
            record = {
                "DATA": data.strftime('%Y-%m-%d'),
                "HOSPITAL": st.text_input("Hospital"),
                "CONV": st.text_input("Convênio"),
                "NOME": st.text_input("Nome"),
                "REG_HOSP": st.text_input("Registro Hospitalar"),
                "CART_INSC": st.text_input("Carteira/Inscrição"),
                "ACOMODACAO": st.text_input("Acomodação"),
                "DATA_DE_NASC": data_de_nasc.strftime('%Y-%m-%d'),
                "IDADE_EM_ANOS": st.number_input("Idade em Anos"),
                "ALTURA_EM_METROS": st.number_input("Altura em Metros"),
                "PESO_EM_Kg": st.number_input("Peso em Kg"),
                "DOENCAS_PRE_EXISTENTES": st.text_area("Doenças Pré-Existentes"),
                "ALERGIAS_INTOLERANCIAS": st.text_area("Alergias/Intolerâncias"),
                "CONDICOES_CLINICAS_LABORATORIAIS_PRE_OPERATORIA": st.text_area(
                    "Condições Clínicas/Laboratoriais Pré Operatória",
                    value="Ht%: , Hb: , Plaquetas: , Glicose: , ABO(Rh): , INR: , K+: , Na+: , E.A.S: , Ureia: , Creatina: , Imunologia: , ECO: FE(%): "
                ),
                "DIAGNOSTICO_PRE_OPERAT": st.text_input("Diagnóstico Pré Operatório"),
                "CIRURGIAS_REALIZADAS": st.text_area("Cirurgias Realizadas"),
                "EQUIPE": st.text_area(
                    "Equipe",
                    value="Cirurgião: , Primeiro Auxiliar: , Segundo Auxiliar: , Anestesista: , Perfusionista: , Instrumentador: , Circulante: "
                ),
                "PACIENTE_RECEBEU_HEMOTRANSFUSAO_EM_SALA": st.selectbox("Paciente recebeu hemotransfusão em sala?", ["Sim", "Não"]),
                "QUAIS": st.text_area("Quais"),
                "DADOS_CEC": st.text_area(
                    "Dados/CEC",
                    value="Tempo de CEC: , Tempo de Clamp: , PCT/APC: "
                ),
            }
            if st.button("Adicionar Dados"):
                response = requests.post(f"{API_URL}/add_record", json=record)
                if response.status_code == 201:
                    st.success("Dados adicionados com sucesso!")
                else:
                    st.error("Falha ao adicionar dados.")

        elif option == "Ver Dados":
            st.subheader("Ver Dados")
            
            st.sidebar.subheader("Filtros")
            filter_name = st.sidebar.text_input("Nome do Paciente")
            filter_hospital = st.sidebar.text_input("Hospital")
            
            apply_filters = st.sidebar.button("Aplicar Filtros")
            clear_filters = st.sidebar.button("Remover Filtros")

            response = requests.get(f"{API_URL}/get_records")
            if response.status_code == 200:
                records = response.json()
                
                if apply_filters:
                    if filter_name:
                        records = [record for record in records if filter_name.lower() in record["NOME"].lower()]
                    if filter_hospital:
                        records = [record for record in records if filter_hospital.lower() in record["HOSPITAL"].lower()]
                elif clear_filters:
                    st.experimental_rerun()

                records = clean_data(records)
                df = pd.DataFrame(records)
                
                columns_order = [
                    "DATA", "HOSPITAL", "CONV", "NOME", "REG_HOSP", "CART_INSC", 
                    "ACOMODACAO", "DATA_DE_NASC", "IDADE_EM_ANOS", "ALTURA_EM_METROS", 
                    "PESO_EM_Kg", "DOENCAS_PRE_EXISTENTES", "ALERGIAS_INTOLERANCIAS", 
                    "CONDICOES_CLINICAS_LABORATORIAIS_PRE_OPERATORIA", 
                    "DIAGNOSTICO_PRE_OPERAT", "CIRURGIAS_REALIZADAS", "EQUIPE", 
                    "PACIENTE_RECEBEU_HEMOTRANSFUSAO_EM_SALA", "QUAIS", "DADOS_CEC"
                ]
                df = df[columns_order]
                st.table(df)
                
                if st.button("Gerar PDF"):
                    pdf = generate_pdf(df.to_dict(orient='records'))
                    
                    st.download_button(
                        label="Baixar PDF",
                        data=pdf,
                        file_name='records.pdf',
                        mime='application/pdf'
                    )
            else:
                st.error("Falha ao carregar os dados.")

        elif option == "Atualizar Dados":
            st.subheader("Atualizar Dados")
            all_names = get_all_patient_names()
            nome_paciente = st.selectbox("Nome do Paciente", all_names)
            if nome_paciente:
                record = get_record_by_name(nome_paciente)
                if record:
                    record_id = record.get('_id')
                    data = st.date_input("Data", value=pd.to_datetime(record["DATA"]))
                    data_de_nasc = st.date_input("Data de Nascimento", value=pd.to_datetime(record["DATA_DE_NASC"]))
                    updated_record = {
                        "DATA": data.strftime('%Y-%m-%d'),
                        "HOSPITAL": st.text_input("Hospital", value=record["HOSPITAL"]),
                        "CONV": st.text_input("Convênio", value=record["CONV"]),
                        "NOME": st.text_input("Nome", value=record["NOME"]),
                        "REG_HOSP": st.text_input("Registro Hospitalar", value=record["REG_HOSP"]),
                        "CART_INSC": st.text_input("Carteira/Inscrição", value=record["CART_INSC"]),
                        "ACOMODACAO": st.text_input("Acomodação", value=record["ACOMODACAO"]),
                        "DATA_DE_NASC": data_de_nasc.strftime('%Y-%m-%d'),
                        "IDADE_EM_ANOS": st.number_input("Idade em Anos", value=int(record["IDADE_EM_ANOS"])),
                        "ALTURA_EM_METROS": st.number_input("Altura em Metros", value=float(record["ALTURA_EM_METROS"])),
                        "PESO_EM_Kg": st.number_input("Peso em Kg", value=float(record["PESO_EM_Kg"])),
                        "DOENCAS_PRE_EXISTENTES": st.text_area("Doenças Pré-Existentes", value=record["DOENCAS_PRE_EXISTENTES"]),
                        "ALERGIAS_INTOLERANCIAS": st.text_area("Alergias/Intolerâncias", value=record["ALERGIAS_INTOLERANCIAS"]),
                        "CONDICOES_CLINICAS_LABORATORIAIS_PRE_OPERATORIA": st.text_area(
                            "Condições Clínicas/Laboratoriais Pré Operatória",
                            value=record["CONDICOES_CLINICAS_LABORATORIAIS_PRE_OPERATORIA"]
                        ),
                        "DIAGNOSTICO_PRE_OPERAT": st.text_input("Diagnóstico Pré Operatório", value=record["DIAGNOSTICO_PRE_OPERAT"]),
                        "CIRURGIAS_REALIZADAS": st.text_area("Cirurgias Realizadas", value=record["CIRURGIAS_REALIZADAS"]),
                        "EQUIPE": st.text_area(
                            "Equipe",
                            value=record["EQUIPE"]
                        ),
                        "PACIENTE_RECEBEU_HEMOTRANSFUSAO_EM_SALA": st.selectbox("Paciente recebeu hemotransfusão em sala?", ["Sim", "Não"], index=["Sim", "Não"].index(record["PACIENTE_RECEBEU_HEMOTRANSFUSAO_EM_SALA"])),
                        "QUAIS": st.text_area("Quais", value=record["QUAIS"]),
                        "DADOS_CEC": st.text_area(
                            "Dados/CEC",
                            value=record["DADOS_CEC"]
                        ),
                    }
                    if st.button("Atualizar Dados"):
                        response = requests.put(f"{API_URL}/update_record/{record_id}", json=updated_record)
                        if response.status_code == 200:
                            st.success("Dados atualizados com sucesso!")
                        else:
                            st.error("Falha ao atualizar dados.")
                else:
                    st.error("Paciente não encontrado.")

        elif option == "Deletar Dados":
            st.subheader("Deletar Dados")
            all_names = get_all_patient_names()
            nome_paciente = st.selectbox("Nome do Paciente", all_names)
            if nome_paciente:
                record = get_record_by_name(nome_paciente)
                if record:
                    record_id = record.get('_id')
                    if st.button("Delete"):
                        response = requests.delete(f"{API_URL}/delete_record/{record_id}")
                        if response.status_code == 200:
                            st.success("Dados deletados com sucesso!")
                        else:
                            st.error("Falha ao deletar dados.")
                else:
                    st.error("Paciente não encontrado.")

if __name__ == "__main__":
    main()
