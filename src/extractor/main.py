# main.py

from flask import Flask, request, jsonify
from fetcher import fetch_and_extract_text
from chunker import chunk_text
import uuid
import time

app = Flask(__name__)

# Stockage des sessions en mémoire
sessions = {}

SESSION_TIMEOUT = 15 * 60  # 15 minutes en secondes

@app.route('/process', methods=['POST'])
def process_link():
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({"error": "L'URL est requise."}), 400
    url = data['url']
    try:
        text = fetch_and_extract_text(url)
        chunks = chunk_text(text)
        total_chunks = len(chunks)
        
        # Générer un ID de session unique
        session_id = str(uuid.uuid4())
        # Stocker les données de la session
        sessions[session_id] = {
            'chunks': chunks,
            'timestamp': time.time(),
            'force': False
        }
        
        if total_chunks >= 5:
            # Retourner le message et l'ID de session
            return jsonify({
                "message": "Le fichier est trop volumineux, êtes-vous sûr ?",
                "session_id": session_id,
                "total_chunks": total_chunks
            })
        else:
            # Retourner le premier segment avec le numéro du segment
            first_chunk = chunks[0]
            chunk_number = 1
            response_text = f"{chunk_number}/{total_chunks}\n{first_chunk}\n{chunk_number}/{total_chunks}"
            return jsonify({
                "chunk": response_text,
                "session_id": session_id
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/reply', methods=['POST'])
def handle_reply():
    data = request.get_json()
    if not data or 'session_id' not in data or 'message' not in data:
        return jsonify({"error": "L'ID de session et le message sont requis."}), 400
    
    session_id = data['session_id']
    message = data['message'].strip()
    
    # Nettoyer les sessions expirées
    current_time = time.time()
    expired_sessions = [sid for sid, session_data in sessions.items() if current_time - session_data['timestamp'] > SESSION_TIMEOUT]
    for sid in expired_sessions:
        del sessions[sid]
    
    if session_id not in sessions:
        return jsonify({"error": "ID de session invalide ou expiré."}), 400
    
    session = sessions[session_id]
    session['timestamp'] = current_time  # Mettre à jour le timestamp pour prolonger la session
    
    chunks = session['chunks']
    total_chunks = len(chunks)
    
    if not session.get('force') and message.upper() == 'FORCE YES':
        session['force'] = True
        # Retourner le premier segment
        first_chunk = chunks[0]
        chunk_number = 1
        response_text = f"{chunk_number}/{total_chunks}\n{first_chunk}\n{chunk_number}/{total_chunks}"
        return jsonify({
            "chunk": response_text
        })
    elif session.get('force'):
        # L'utilisateur demande un segment
        # Essayer d'analyser le message comme numéro_du_segment/total_segments
        try:
            if '/' in message:
                chunk_number_str, total_chunks_str = message.split('/')
                chunk_number = int(chunk_number_str)
                if chunk_number < 1 or chunk_number > total_chunks:
                    raise ValueError()
                chunk = chunks[chunk_number - 1]
                response_text = f"{chunk_number}/{total_chunks}\n{chunk}\n{chunk_number}/{total_chunks}"
                return jsonify({
                    "chunk": response_text
                })
            else:
                raise ValueError()
        except ValueError:
            return jsonify({"error": "Format de numéro de segment invalide. Veuillez envoyer 'n/n' où n est le numéro du segment."}), 400
    else:
        # L'utilisateur n'a pas encore confirmé pour continuer
        return jsonify({"error": "Veuillez confirmer pour continuer en envoyant 'FORCE YES'."}), 400

if __name__ == '__main__':
    app.run(debug=True)

