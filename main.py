import os
import time
import requests

# ==============================================================================
# CONFIGURAÇÕES OFICIAIS DO SEU BOT E DA SUA SALA
# ==============================================================================
# ID da sua nova sala configurada
CHAT_ID_TELEGRAM = "-1003895120098"

# URL da API da Blaze oficial para jogos recentes
API_BLAZE = "https://blaze.com"
ARQUIVO_MAXIMA = "maxima.txt"


def carregar_maxima_salva():
    if not os.path.exists(ARQUIVO_MAXIMA):
        return 150
    try:
        with open(ARQUIVO_MAXIMA, "r") as f:
            return int(f.read().strip())
    except Exception:
        return 150


def salvar_nova_maxima(nova_maxima):
    try:
        with open(ARQUIVO_MAXIMA, "w") as f:
            f.write(str(nova_maxima))
    except Exception:
        pass


def enviar_alerta_telegram(mensagem):
    """Envia a notificação usando o seu Bot Oficial direto para a sua Sala."""
    url_limpa = "https://telegram.org"
    payload = {
        "chat_id": CHAT_ID_TELEGRAM,
        "text": mensagem,
        "parse_mode": "Markdown"
    }
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.post(url_limpa, json=payload, headers=headers, timeout=10)
        if response.status_code == 200:
            print("📬 [Render] Alerta enviado com sucesso para a sala!")
        else:
            print(f"⚠️ Telegram recusou o envio. Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro de rede ao enviar para o Telegram: {e}")


def analisar_comportamento(historico_rodadas, maxima_atual_salva):
    cores = []
    for r in historico_rodadas:
        if isinstance(r, dict):
            cor = r.get("color")
            if cor in [0, "white", "W"]: cores.append("white")
            elif cor in [1, "red", "R"]: cores.append("red")
            else: cores.append("black")

    indices_brancos = [i for i, c in enumerate(cores) if c == "white"]
    indices_eventos_confirmados = []
    for i in range(len(indices_brancos) - 1):
        distancia = indices_brancos[i + 1] - indices_brancos[i]
        if 1 <= distancia <= 5: 
            indices_eventos_confirmados.append(indices_brancos[i + 1])

    if not indices_eventos_confirmados:
        return 0, maxima_atual_salva, 0

    gaps_de_espera = [indices_eventos_confirmados[i + 1] - indices_eventos_confirmados[i] for i in range(len(indices_eventos_confirmados) - 1)]
    maxima_do_lote = max(gaps_de_espera) if gaps_de_espera else 0
    maxima_historica = max(maxima_do_lote, maxima_atual_salva)
    
    if maxima_historica > maxima_atual_salva:
        salvar_nova_maxima(maxima_historica)

    distancia_atual = len(cores) - indices_eventos_confirmados[-1]
    porcentagem_proximidade = (distancia_atual / maxima_historica) * 100 if maxima_historica > 0 else 0
    return distancia_atual, maxima_historica, porcentagem_proximidade


if __name__ == "__main__":
    print("🚀 Robô da Blaze Oficial Iniciado no Render!")
    
    msg_inicial = (
        "🔌 *Rastreador Online no Servidor!*\n\n"
        "O monitoramento da roleta foi iniciado com sucesso na nuvem sem bloqueios.\n"
        "🎯 *Configuração:* Buscando Brancos em até 5 casas com gatilho de *90%*."
    )
    enviar_alerta_telegram(msg_inicial)
    
    ultimo_id_visto = None

    while True:
        try:
            response = requests.get(API_BLAZE, timeout=10)
            if response.status_code == 200:
                dados_blaze = response.json()[::-1]
                
                id_recente = dados_blaze[-1].get("id")
                if id_recente != ultimo_id_visto:
                    ultimo_id_visto = id_recente
                    
                    maxima_carregada = carregar_maxima_salva()
                    dist_atual, max_hist, proximidade = analisar_comportamento(dados_blaze, maxima_carregada)
                    print(f"📊 [Status] Atual: {dist_atual} rodadas | Máxima: {max_hist} | Prox: {proximidade:.1f}%")
                    
                    if proximidade >= 90.0:
                        mensagem = (
                            "⚠️ *ALERTA DE PROXIMIDADE BLAZE (90%)* ⚠️\n\n"
                            "O padrão *Branco com intervalo de até 5 casas* atingiu a zona crítica!\n\n"
                            f"📊 *Atraso Atual:* {dist_atual} rodadas sem acontecer\n"
                            f"📈 *Máxima Registrada:* {max_hist} rodadas\n"
                            f"🔥 *Proximidade:* {proximidade:.1f}%\n\n"
                            "🎯 *Ação:* Inicie suas entradas para buscar a repetição curta!"
                        )
                        enviar_alerta_telegram(mensagem)
                        time.sleep(240)
        except Exception as e:
            print(f"🔄 Conexão instável com a Blaze, reconectando... ({e})")
            
        time.sleep(15)
