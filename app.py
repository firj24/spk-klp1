from flask import Flask, render_template, request, redirect, url_for, flash
import pandas as pd
import numpy as np
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './uploads'
app.secret_key = 'your_secret_key'  # Untuk flash message

# Pastikan folder upload ada
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

CSV_PATH = os.path.join(app.config['UPLOAD_FOLDER'], 'data.csv')  # Path file CSV

# Route untuk halaman upload
@app.route('/')
def upload_file():
    return render_template('upload.html')

# Route untuk memproses file CSV
@app.route('/process', methods=['POST'])
def process_file():
    if 'file' not in request.files:
        flash("No file uploaded!")
        return redirect(url_for('upload_file'))

    file = request.files['file']
    if file.filename == '':
        flash("No file selected!")
        return redirect(url_for('upload_file'))

    if not file.filename.endswith('.csv'):
        flash("Invalid file type! Please upload a CSV file.")
        return redirect(url_for('upload_file'))

    file.save(CSV_PATH)

    flash("File uploaded successfully!")
    return redirect(url_for('process_data'))

# Route untuk memproses AHP dan WP
@app.route('/process_data')
def process_data():
    if not os.path.exists(CSV_PATH):
        flash("No data to process! Please upload a CSV file first.")
        return redirect(url_for('upload_file'))

    try:
        # Baca file CSV
        data = pd.read_csv(CSV_PATH)

        # Validasi kolom
        expected_columns = [
            "alternatif",
            "Laju Pertumbuhan Kumulatif (c-to-c)",
            "Laju Pertumbuhan Triwulanan Berantai (q-to-q)",
            "Laju Pertumbuhan Triwulanan terhadap Triwulan yang Sama Tahun Sebelumnya (y-on-y)",
            "Inflasi",
            "Pengangguran"
        ]
        if not all(col in data.columns for col in expected_columns):
            flash("CSV file missing required columns!")
            return redirect(url_for('upload_file'))

        # AHP dan WP
        benefit_columns = expected_columns[1:-1]
        cost_columns = ["Pengangguran"]
        bobot = np.array([0.412444147113247, 0.244636824257982, 0.190935782276034, 0.0908352412141844, 0.0611480051385523])

        # Normalisasi
        normalized_data = data.copy()
        for column in benefit_columns:
            normalized_data[column] = data[column] / data[column].max()
        for column in cost_columns:
            normalized_data[column] = data[column].min() / data[column]

        # WP Perhitungan Preferensi
        preferences = (normalized_data.iloc[:, 1:] ** bobot).prod(axis=1)
        normalized_data["Preferensi"] = preferences
        normalized_data["Rank"] = normalized_data["Preferensi"].rank(ascending=False)

        # Hasil
        results = normalized_data[["alternatif", "Preferensi", "Rank"]].sort_values(by="Rank")

        return render_template('result.html', tables=[results.to_html(classes='data')], titles=results.columns.values)

    except Exception as e:
        flash(f"Error processing data: {e}")
        return redirect(url_for('upload_file'))

# Route untuk halaman tambah alternatif
@app.route('/add_alternatif')
def add_alternatif():
    return render_template('add_alternatif.html')

# Route untuk menyimpan alternatif baru
@app.route('/save_alternatif', methods=['GET','POST'])
def save_alternatif():
    if not os.path.exists(CSV_PATH):
        flash("No data file found! Please upload a CSV file first.")
        return redirect(url_for('upload_file'))

    try:
        # Ambil data dari form
        alternatif = request.form['alternatif']
        c_to_c = float(request.form['c_to_c'])
        q_to_q = float(request.form['q_to_q'])
        y_on_y = float(request.form['y_on_y'])
        inflasi = float(request.form['inflasi'])
        pengangguran = float(request.form['pengangguran'])

        # Tambahkan data baru ke CSV
        new_data = pd.DataFrame([{
            "alternatif": alternatif,
            "Laju Pertumbuhan Kumulatif (c-to-c)": c_to_c,
            "Laju Pertumbuhan Triwulanan Berantai (q-to-q)": q_to_q,
            "Laju Pertumbuhan Triwulanan terhadap Triwulan yang Sama Tahun Sebelumnya (y-on-y)": y_on_y,
            "Inflasi": inflasi,
            "Pengangguran": pengangguran
        }])
        existing_data = pd.read_csv(CSV_PATH)
        updated_data = pd.concat([existing_data, new_data], ignore_index=True)
        updated_data.to_csv(CSV_PATH, index=False)

        flash("New alternative added successfully!")
        return redirect(url_for('process_data'))

    except Exception as e:
        flash(f"Error adding alternative: {e}")
        return redirect(url_for('add_alternatif'))

if __name__ == "__main__":
    app.run(debug=True)
