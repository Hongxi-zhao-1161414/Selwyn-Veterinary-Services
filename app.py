from flask import Flask, render_template, request, redirect, url_for, flash
import db
import connect
from datetime import datetime, date
from decimal import Decimal

app = Flask(__name__)
app.secret_key = 'svs_secret_2025_secure_key' 


db.init_db(
    app, connect.dbuser, connect.dbpass, connect.dbhost, connect.dbname, connect.dbport
)



@app.route("/")
def home():
    return render_template("home.html")


@app.route("/services", methods=["GET"])
def service_list():
    cursor = db.get_cursor()
    try:
        query = "SELECT service_id, service_name, price FROM services ORDER BY service_name ASC;"
        cursor.execute(query)
        services = cursor.fetchall()
        flash("Services loaded successfully!", "info")
    except Exception as e:
        flash(f"Error loading services: {str(e)}", "danger")
        services = []
    finally:
        cursor.close()
    return render_template("service_list.html", services=services)


@app.route("/customers")
def customer_list():
    cursor = db.get_cursor()
    try:
        query = """
            SELECT customer_id, first_name, family_name, email, phone, date_joined 
            FROM customers 
            ORDER BY family_name ASC, first_name ASC;
        """
        cursor.execute(query)
        customers = cursor.fetchall()
        # 转换日期格式为NZ格式（dd/mm/yyyy）
        for customer in customers:
            customer['date_joined'] = customer['date_joined'].strftime('%d/%m/%Y')
    except Exception as e:
        flash(f"Error loading customers: {str(e)}", "danger")
        customers = []
    finally:
        cursor.close()
    return render_template("customer_list.html", customers=customers)


@app.route("/customers/search", methods=["GET"])
def customer_search():
    """客户搜索页：支持名字/姓氏的部分匹配"""
    search_term = request.args.get('search_term', '').strip()
    customers = []
    if search_term:
        cursor = db.get_cursor()
        try:
            # 部分匹配（不区分大小写）
            query = """
                SELECT customer_id, first_name, family_name, email, phone, date_joined 
                FROM customers 
                WHERE first_name LIKE %s OR family_name LIKE %s 
                ORDER BY family_name ASC, first_name ASC;
            """
            # 拼接%实现模糊查询
            like_term = f'%{search_term}%'
            cursor.execute(query, (like_term, like_term))
            customers = cursor.fetchall()
            # 转换日期格式
            for customer in customers:
                customer['date_joined'] = customer['date_joined'].strftime('%d/%m/%Y')
            flash(f"Found {len(customers)} customer(s) matching '{search_term}'", "info")
        except Exception as e:
            flash(f"Error searching customers: {str(e)}", "danger")
        finally:
            cursor.close()
    else:
        flash("Please enter a search term (first name or family name)", "warning")
    return render_template("customer_search.html", customers=customers, search_term=search_term)


@app.route("/customers/add", methods=["GET", "POST"])
def add_customer():
    """新增客户页：GET显示表单，POST处理提交"""
    if request.method == "POST":
        # 获取表单数据
        first_name = request.form.get('first_name', '').strip()
        family_name = request.form.get('family_name', '').strip()
        email = request.form.get('email', '').strip()  # 可选
        phone = request.form.get('phone', '').strip()
        date_joined_str = request.form.get('date_joined', '')

        # 数据验证
        errors = []
        if not first_name:
            errors.append("First name is required")
        if not family_name:
            errors.append("Family name is required")
        if not phone:
            errors.append("Phone number is required")
        try:
            date_joined = datetime.strptime(date_joined_str, '%Y-%m-%d').date()
            if date_joined > date.today():
                errors.append("Date joined cannot be in the future")
        except ValueError:
            errors.append("Invalid date format (use YYYY-MM-DD)")

        # 验证失败：返回表单并显示错误
        if errors:
            for error in errors:
                flash(error, "danger")
            today = date.today().strftime('%Y-%m-%d')
            return render_template("add_customer.html", today=today)

        # 验证成功：插入数据库
        cursor = db.get_cursor()
        try:
            query = """
                INSERT INTO customers (first_name, family_name, email, phone, date_joined)
                VALUES (%s, %s, %s, %s, %s);
            """
            cursor.execute(query, (first_name, family_name, email, phone, date_joined))
            flash(f"Customer {first_name} {family_name} added successfully!", "success")
            return redirect(url_for('customer_list'))
        except Exception as e:
            flash(f"Error adding customer: {str(e)}", "danger")
        finally:
            cursor.close()

    # GET请求：显示表单（默认日期为今天）
    today = date.today().strftime('%Y-%m-%d')
    return render_template("add_customer.html", today=today)


@app.route("/customers/edit/<int:customer_id>", methods=["GET", "POST"])
def edit_customer(customer_id):
    """编辑客户页：GET加载客户信息，POST更新数据"""
    # GET请求：加载客户信息
    if request.method == "GET":
        cursor = db.get_cursor()
        try:
            query = "SELECT * FROM customers WHERE customer_id = %s;"
            cursor.execute(query, (customer_id,))
            customer = cursor.fetchone()
            if not customer:
                flash(f"Customer with ID {customer_id} not found", "danger")
                return redirect(url_for('customer_list'))
            # 转换日期格式为HTML date输入支持的格式（YYYY-MM-DD）
            customer['date_joined_html'] = customer['date_joined'].strftime('%Y-%m-%d')
            # 转换显示用的日期格式（dd/mm/yyyy）
            customer['date_joined_display'] = customer['date_joined'].strftime('%d/%m/%Y')
            return render_template("edit_customer.html", customer=customer)
        except Exception as e:
            flash(f"Error loading customer: {str(e)}", "danger")
            return redirect(url_for('customer_list'))
        finally:
            cursor.close()

    # POST请求：处理更新
    if request.method == "POST":
        first_name = request.form.get('first_name', '').strip()
        family_name = request.form.get('family_name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()

        # 数据验证（不允许修改ID和date_joined）
        errors = []
        if not first_name:
            errors.append("First name is required")
        if not family_name:
            errors.append("Family name is required")
        if not phone:
            errors.append("Phone number is required")

        if errors:
            for error in errors:
                flash(error, "danger")
            # 重新加载客户信息（保持表单填充）
            cursor = db.get_cursor()
            cursor.execute("SELECT * FROM customers WHERE customer_id = %s;", (customer_id,))
            customer = cursor.fetchone()
            customer['date_joined_html'] = customer['date_joined'].strftime('%Y-%m-%d')
            customer['date_joined_display'] = customer['date_joined'].strftime('%d/%m/%Y')
            cursor.close()
            return render_template("edit_customer.html", customer=customer)

        # 执行更新
        cursor = db.get_cursor()
        try:
            query = """
                UPDATE customers 
                SET first_name = %s, family_name = %s, email = %s, phone = %s 
                WHERE customer_id = %s;
            """
            cursor.execute(query, (first_name, family_name, email, phone, customer_id))
            flash(f"Customer {first_name} {family_name} updated successfully!", "success")
            return redirect(url_for('customer_list'))
        except Exception as e:
            flash(f"Error updating customer: {str(e)}", "danger")
            # 重新加载表单
            cursor.execute("SELECT * FROM customers WHERE customer_id = %s;", (customer_id,))
            customer = cursor.fetchone()
            customer['date_joined_html'] = customer['date_joined'].strftime('%Y-%m-%d')
            customer['date_joined_display'] = customer['date_joined'].strftime('%d/%m/%Y')
            return render_template("edit_customer.html", customer=customer)
        finally:
            cursor.close()


# ------------------- 预约相关路由 -------------------
def _process_appointment_data(rows):
    """辅助函数：处理预约查询结果，按预约ID分组并计算总费用"""
    appointments = {}
    for row in rows:
        appt_id = row['appt_id']
        if appt_id not in appointments:
            # 初始化预约基础信息：total_cost改为Decimal类型
            appointments[appt_id] = {
                'appt_id': appt_id,
                'appt_datetime': row['appt_datetime'],
                'appt_datetime_display': row['appt_datetime'].strftime('%d/%m/%Y %H:%M'),
                'notes': row['notes'] or 'No notes',
                'first_name': row['first_name'],
                'family_name': row['family_name'],
                'services': [],
                'total_cost': Decimal('0.0')  # 关键修改：从0.0改为Decimal('0.0')
            }
        # 添加服务信息（price是Decimal类型，直接使用）
        service = {
            'service_name': row['service_name'],
            'price': row['price'],
            'price_display': f"${row['price']:.2f}"  # Decimal支持f-string格式化
        }
        appointments[appt_id]['services'].append(service)
        # 累加总费用：此时两边都是Decimal类型，可正常运算
        appointments[appt_id]['total_cost'] += row['price']
        # 格式化总费用（Decimal直接用f-string即可）
        appointments[appt_id]['total_cost_display'] = f"${appointments[appt_id]['total_cost']:.2f}"
    return list(appointments.values())


@app.route("/appointments")
def appointment_list():
    """预约列表页：显示所有预约（按时间从旧到新），未来预约标绿"""
    cursor = db.get_cursor()
    try:
        # 多表连接查询：预约+客户+服务
        query = """
             SELECT a.appt_id, a.appt_datetime, a.notes, 
                   c.first_name, c.family_name, 
                   s.service_name, s.price
            FROM appointments a
            JOIN customers c ON a.customer_id = c.customer_id
            JOIN appointment_services asv ON a.appt_id = asv.appt_id  
            JOIN services s ON asv.service_id = s.service_id          
            ORDER BY a.appt_datetime ASC;
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        appointments = _process_appointment_data(rows)
        # 当前时间（用于判断未来预约）
        now = datetime.now()
    except Exception as e:
        flash(f"Error loading appointments: {str(e)}", "danger")
        appointments = []
        now = datetime.now()
    finally:
        cursor.close()
    return render_template("appointment_list.html", appointments=appointments, now=now)


@app.route("/appointments/new", methods=["GET", "POST"])
def new_appointment():
    """新增预约页：GET显示表单，POST处理提交"""
    # 加载客户和服务列表（GET和POST失败时均需）
    def load_form_data():
        cursor = db.get_cursor()
        # 加载客户（按姓氏排序）
        cursor.execute("SELECT customer_id, first_name, family_name FROM customers ORDER BY family_name ASC;")
        customers = cursor.fetchall()
        # 加载服务（按名称排序）
        cursor.execute("SELECT service_id, service_name, price FROM services ORDER BY service_name ASC;")
        services = cursor.fetchall()
        cursor.close()
        return customers, services

    if request.method == "POST":
        # 获取表单数据
        customer_id = request.form.get('customer_id')
        appt_datetime_str = request.form.get('appt_datetime')
        notes = request.form.get('notes', '').strip()
        selected_services = request.form.getlist('services')  # 多选服务

        # 数据验证
        errors = []
        if not customer_id:
            errors.append("Please select a customer")
        if not appt_datetime_str:
            errors.append("Please select an appointment date and time")
        if not selected_services:
            errors.append("At least one service must be selected")

        # 验证日期时间
        appt_datetime = None
        if appt_datetime_str:
            try:
                # 解析datetime-local格式（YYYY-MM-DDTHH:MM）
                appt_datetime = datetime.strptime(appt_datetime_str, '%Y-%m-%dT%H:%M')
                # 检查是否为未来时间
                if appt_datetime <= datetime.now():
                    errors.append("Appointment date and time must be in the future")
                # 检查是否为周日（weekday()：0=周一，6=周日）
                if appt_datetime.weekday() == 6:
                    errors.append("Appointments cannot be scheduled on Sundays")
            except ValueError:
                errors.append("Invalid date/time format")

        # 验证失败
        if errors:
            for error in errors:
                flash(error, "danger")
            customers, services = load_form_data()
            return render_template("new_appointment.html", customers=customers, services=services)

        # 验证成功：插入数据库（事务：先插预约，再插服务关联）
        cursor = db.get_cursor()
        db_conn = db.get_db()  # 获取连接以控制事务
        try:
            db_conn.autocommit = False  # 关闭自动提交，开启事务

            # 1. 插入预约表，获取新预约ID
            insert_appt_query = """
                INSERT INTO appointments (customer_id, appt_datetime, notes)
                VALUES (%s, %s, %s);
            """
            cursor.execute(insert_appt_query, (customer_id, appt_datetime, notes))
            new_appt_id = cursor.lastrowid  # 获取自增的appt_id

            # 2. 插入预约-服务关联表（每个服务一条记录）
            insert_as_query = """
                INSERT INTO appointment_services (appt_id, service_id)
                VALUES (%s, %s);
            """
            for service_id in selected_services:
                cursor.execute(insert_as_query, (new_appt_id, service_id))

            db_conn.commit()  # 提交事务
            flash(f"Appointment scheduled successfully! (ID: {new_appt_id})", "success")
            return redirect(url_for('appointment_list'))
        except Exception as e:
            db_conn.rollback()  # 回滚事务
            flash(f"Error scheduling appointment: {str(e)}", "danger")
        finally:
            db_conn.autocommit = True  # 恢复自动提交
            cursor.close()

    # GET请求：显示表单
    customers, services = load_form_data()
    return render_template("new_appointment.html", customers=customers, services=services)


@app.route("/customer/<int:customer_id>/appointments")
def customer_appointment_summary(customer_id):
    """客户预约汇总页：显示指定客户的所有预约"""
    # 先获取客户姓名（用于页面标题）
    cursor = db.get_cursor()
    customer_name = "Unknown Customer"
    try:
        cursor.execute("SELECT first_name, family_name FROM customers WHERE customer_id = %s;", (customer_id,))
        customer = cursor.fetchone()
        if customer:
            customer_name = f"{customer['first_name']} {customer['family_name']}"
        else:
            flash(f"Customer with ID {customer_id} not found", "danger")
            return redirect(url_for('customer_list'))
    except Exception as e:
        flash(f"Error loading customer info: {str(e)}", "danger")
        return redirect(url_for('customer_list'))

    # 查询该客户的所有预约
    try:
        query = """
            SELECT a.appt_id, a.appt_datetime, a.notes, 
           c.first_name, c.family_name, 
           s.service_name, s.price
            FROM appointments a
            JOIN customers c ON a.customer_id = c.customer_id
            JOIN appointment_services asv ON a.appt_id = asv.appt_id  
            JOIN services s ON asv.service_id = s.service_id         
            WHERE a.customer_id = %s
            ORDER BY a.appt_datetime ASC;
        """
        cursor.execute(query, (customer_id,))
        rows = cursor.fetchall()
        appointments = _process_appointment_data(rows)
        now = datetime.now()
    except Exception as e:
        flash(f"Error loading {customer_name}'s appointments: {str(e)}", "danger")
        appointments = []
        now = datetime.now()
    finally:
        cursor.close()

    return render_template(
        "customer_appointment_summary.html",
        customer_name=customer_name,
        appointments=appointments,
        now=now,
        customer_id=customer_id
    )


# ------------------- 报告相关路由 -------------------
@app.route("/service-summary-report")
def service_summary_report():
    """服务汇总报告：显示每个服务的使用次数和总收益"""
    cursor = db.get_cursor()
    try:
        query = """
             SELECT s.service_id, s.service_name, s.price,
           COUNT(asv.service_id) as service_count,  
           SUM(s.price) as total_earnings
            FROM services s
            LEFT JOIN appointment_services asv ON s.service_id = asv.service_id  
            GROUP BY s.service_id, s.service_name, s.price
            ORDER BY s.service_name ASC;
        """
        cursor.execute(query)
        services = cursor.fetchall()
        # 格式化数值显示：处理Decimal和None
        for service in services:
            # price是Decimal，直接格式化
            service['price_display'] = f"${service['price']:.2f}"
            # total_earnings可能是None（无数据），转为Decimal('0.0')再格式化
            total_earnings = service['total_earnings'] or Decimal('0.0')
            service['total_earnings_display'] = f"${total_earnings:.2f}"
    except Exception as e:
        flash(f"Error generating service report: {str(e)}", "danger")
        services = []
    finally:
        cursor.close()
    return render_template("service_summary_report.html", services=services)


if __name__ == "__main__":
    app.run(debug=True) 