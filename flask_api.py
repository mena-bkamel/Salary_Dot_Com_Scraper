import csv
import io
import sqlite3
import json
from flask import Flask, jsonify, request, render_template, Response

DB_PATH = "salary_results.db"
TABLE = "salary"
percentile = ['nTile10', 'nTile25', 'nTile50', 'nTile75', 'nTile90']

app = Flask(__name__)


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# Get all jobs
@app.route("/api/jobs", methods=["GET"])
def get_all_jobs():
    conn = get_db_connection()

    try:
        jobs = conn.execute(f"SELECT * FROM {TABLE}").fetchall()
        conn.close()
        return jsonify([dict(row) for row in jobs]), 200

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        conn.close()
        return jsonify({"error": "An error occurred while retrieving jobs."}), 500


# Get Jobs by Title
@app.route('/api/jobs/title/<string:job_title>', methods=['GET'])
def get_jobs_by_title(job_title):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {TABLE} WHERE job_title LIKE ?",
                       ('%' + job_title + '%',))
        jobs = cursor.fetchall()
        conn.close()
        return jsonify([dict(row) for row in jobs]), 200

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        conn.close()
        return jsonify({"error": "An error occurred while retrieving jobs."}), 500

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        conn.close()
        return jsonify({"error": "An unexpected error occurred."}), 500


#  Get Jobs by City
@app.route('/api/jobs/city/<string:city>', methods=['GET'])
def get_jobs_by_city(city):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {TABLE} WHERE job_location LIKE ?",
                       ('%' + city + '%',))
        jobs = cursor.fetchall()
        conn.close()

        return jsonify([dict(row) for row in jobs]), 200

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        conn.close()
        return jsonify({"error": "An error occurred while retrieving jobs."}), 500

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        conn.close()
        return jsonify({"error": "An unexpected error occurred."}), 500


# Get Salary Percentiles for a Job in a City
@app.route('/api/jobs/salary/<string:job_title>/<string:city>', methods=['GET'])
def get_salary_for_job_city(job_title, city):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        percentile_columns = ", ".join(percentile)
        cursor.execute(
            f"SELECT job_title, job_location, {percentile_columns} FROM {TABLE} WHERE job_title LIKE ? AND job_location LIKE ?",
            ('%' + job_title + '%', '%' + city + '%')
        )
        job = cursor.fetchone()
        conn.close()

        if job:
            return jsonify(dict(job)), 200
        else:
            return jsonify({"error": "No data found"}), 404

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        conn.close()
        return jsonify({"error": "An error occurred while retrieving data."}), 500

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        conn.close()
        return jsonify({"error": "An unexpected error occurred."}), 500


#  Get Highest Paying Jobs in a City
@app.route('/api/jobs/top_paying/<string:city>', methods=['GET'])
def get_top_paying_jobs(city):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            f"SELECT job_title, job_location, {percentile[-1]} FROM {TABLE} WHERE job_location LIKE ? ORDER BY nTile90 DESC LIMIT 10",
            ('%' + city + '%',)
        )
        jobs = cursor.fetchall()
        conn.close()

        return render_template("index.html")

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        conn.close()
        return render_template("index.html")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        conn.close()
        return render_template("index.html")


# Get Jobs in a Salary Range
@app.route('/api/jobs/salary_range', methods=['GET'])
def get_jobs_by_salary_range():
    conn = get_db_connection()
    try:
        min_salary = request.args.get('min', type=float, default=0)
        max_salary = request.args.get('max', type=float, default=1e9)

        cursor = conn.cursor()
        cursor.execute(
            f"SELECT * FROM {TABLE} WHERE nTile50 BETWEEN ? AND ?",
            (min_salary, max_salary)
        )
        jobs = cursor.fetchall()
        conn.close()

        return jsonify([dict(job) for job in jobs])

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        conn.close()
        return jsonify({"error": "An error occurred while retrieving data."}), 500

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        conn.close()
        return jsonify({"error": "An unexpected error occurred."}), 500


# Get Jobs with Highest Growth Potential
@app.route('/api/jobs/high_growth', methods=['GET'])
def get_high_growth_jobs():
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            f"SELECT job_title, job_location, (nTile90 - nTile10) AS salary_growth FROM {TABLE} ORDER BY salary_growth DESC LIMIT 10"
        )
        jobs = cursor.fetchall()
        conn.close()

        return jsonify([dict(job) for job in jobs])

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        conn.close()
        return jsonify({"error": "An error occurred while retrieving data."}), 500

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        conn.close()
        return jsonify({"error": "An unexpected error occurred."}), 500


# Pagination Support
@app.route('/api/jobs/paginate', methods=['GET'])
def get_paginated_jobs():
    conn = get_db_connection()
    try:
        page = request.args.get('page', type=int, default=1)
        per_page = request.args.get('per_page', type=int, default=10)
        offset = (page - 1) * per_page

        cursor = conn.cursor()
        cursor.execute(
            f"SELECT * FROM {TABLE} LIMIT ? OFFSET ?",
            (per_page, offset)
        )
        jobs = cursor.fetchall()
        conn.close()

        return jsonify([dict(job) for job in jobs])

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        conn.close()
        return jsonify({"error": "An error occurred while retrieving data."}), 500

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        conn.close()
        return jsonify({"error": "An unexpected error occurred."}), 500


@app.route('/api/export/csv', methods=['GET'])
def export_csv():
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {TABLE}")
        jobs = cursor.fetchall()
        conn.close()

        # Create an in-memory stream for CSV output
        output = io.StringIO()
        writer = csv.writer(output)

        # Write header row
        writer.writerow(
            ["job_title", "job_location", "job_description", "nTile10", "nTile25", "nTile50", "nTile75", "nTile90"])

        # Write data rows
        for job in jobs:
            writer.writerow([
                job['job_title'],
                job['job_location'],
                job['job_description'],
                job['nTile10'],
                job['nTile25'],
                job['nTile50'],
                job['nTile75'],
                job['nTile90']
            ])

        output.seek(0)  # Seek to the beginning of the stream
        return Response(output, mimetype='text/csv',
                        headers={"Content-Disposition": "attachment; filename=salary_data.csv"})

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        conn.close()
        return jsonify({"error": "An error occurred while retrieving data."}), 500

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        conn.close()
        return jsonify({"error": "An unexpected error occurred."}), 500


@app.route('/api/export/json', methods=['GET'])
def export_json():
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {TABLE}")
        jobs = cursor.fetchall()
        conn.close()

        json_data = [dict(job) for job in jobs]
        response = Response(
            response=json.dumps(json_data, indent=4),
            mimetype="application/json",
            headers={"Content-Disposition": "attachment; filename=salary_data.json"}
        )
        return response

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        conn.close()
        return jsonify({"error": "An error occurred while retrieving data."}), 500

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        conn.close()
        return jsonify({"error": "An unexpected error occurred."}), 500


if __name__ == '__main__':
    app.run(debug=True)
