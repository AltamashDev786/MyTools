import uuid
import qrcode
from flask import Flask, render_template, request, send_from_directory
from datetime import date
from werkzeug.utils import secure_filename
import base64
from rembg import remove, new_session
import calendar
import math
import os
import uuid


app = Flask(__name__)

# Load the AI model once when the app starts.
REMBG_SESSION = new_session("u2net")


# =========================
# FOLDERS
# =========================

UPLOAD_FOLDER = os.path.join(
    "static",
    "uploads"
)

REMOVED_FOLDER = os.path.join(
    "static",
    "removed"
)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["REMOVED_FOLDER"] = REMOVED_FOLDER


# Create folders automatically
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(REMOVED_FOLDER, exist_ok=True)


# Allowed image types
ALLOWED_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg",
    "webp"
}


def allowed_file(filename):

    return (
        "." in filename
        and filename.rsplit(
            ".",
            1
        )[1].lower() in ALLOWED_EXTENSIONS
    )


# =========================
# HOME PAGE
# =========================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


# =========================
# CALCULATORS PAGE
# =========================

@app.route("/calculators")
def calculators():

    return render_template(
        "calculators.html"
    )


# =========================
# BASIC CALCULATOR
# =========================

@app.route(
    "/calculator/basic",
    methods=["GET", "POST"]
)
def basic_calculator():

    result = None
    error = None

    if request.method == "POST":

        try:

            number1 = float(
                request.form["number1"]
            )

            number2 = float(
                request.form["number2"]
            )

            operation = request.form["operation"]


            if operation == "add":

                result = number1 + number2


            elif operation == "subtract":

                result = number1 - number2


            elif operation == "multiply":

                result = number1 * number2


            elif operation == "divide":

                if number2 == 0:

                    error = (
                        "Cannot divide by zero."
                    )

                else:

                    result = number1 / number2


        except (ValueError, TypeError):

            error = (
                "Please enter valid numbers."
            )


    return render_template(
        "basic_calculator.html",
        result=result,
        error=error
    )


# =========================
# SCIENTIFIC CALCULATOR
# =========================

@app.route(
    "/calculator/scientific",
    methods=["GET", "POST"]
)
def scientific_calculator():

    result = None
    error = None

    if request.method == "POST":

        expression = request.form.get(
            "expression",
            ""
        ).strip()


        if not expression:

            error = (
                "Please enter a calculation."
            )


        else:

            try:

                expression = expression.replace(
                    "^",
                    "**"
                )


                allowed = {

                    "sin":
                        lambda x:
                        math.sin(
                            math.radians(x)
                        ),

                    "cos":
                        lambda x:
                        math.cos(
                            math.radians(x)
                        ),

                    "tan":
                        lambda x:
                        math.tan(
                            math.radians(x)
                        ),

                    "sqrt":
                        math.sqrt,

                    "log":
                        math.log10,

                    "ln":
                        math.log,

                    "abs":
                        abs,

                    "pi":
                        math.pi,

                    "e":
                        math.e
                }


                result = eval(
                    expression,
                    {"__builtins__": {}},
                    allowed
                )


            except ZeroDivisionError:

                error = (
                    "Cannot divide by zero."
                )


            except (ValueError, TypeError):

                error = (
                    "Invalid calculation."
                )


            except Exception:

                error = (
                    "Please enter a valid expression."
                )


    return render_template(
        "scientific_calculator.html",
        result=result,
        error=error
    )


# =========================
# AGE CALCULATOR
# =========================

@app.route(
    "/calculator/age",
    methods=["GET", "POST"]
)
def age_calculator():

    result = None
    error = None

    today = date.today()


    if request.method == "POST":

        dob_text = request.form.get(
            "dob",
            ""
        ).strip()


        if not dob_text:

            error = (
                "Please select your date of birth."
            )


        else:

            try:

                year, month, day = map(
                    int,
                    dob_text.split("-")
                )


                dob = date(
                    year,
                    month,
                    day
                )


                if dob > today:

                    error = (
                        "Date of birth cannot "
                        "be in the future."
                    )


                else:

                    years = (
                        today.year -
                        dob.year
                    )

                    months = (
                        today.month -
                        dob.month
                    )

                    days = (
                        today.day -
                        dob.day
                    )


                    if days < 0:

                        months -= 1

                        previous_month = (
                            today.month - 1
                        )

                        previous_year = (
                            today.year
                        )


                        if previous_month == 0:

                            previous_month = 12

                            previous_year -= 1


                        days += calendar.monthrange(
                            previous_year,
                            previous_month
                        )[1]


                    if months < 0:

                        years -= 1

                        months += 12


                    total_days = (
                        today - dob
                    ).days


                    next_birthday_year = (
                        today.year
                    )


                    try:

                        next_birthday = date(
                            next_birthday_year,
                            dob.month,
                            dob.day
                        )

                    except ValueError:

                        next_birthday = date(
                            next_birthday_year,
                            2,
                            28
                        )


                    if next_birthday < today:

                        next_birthday_year += 1


                        try:

                            next_birthday = date(
                                next_birthday_year,
                                dob.month,
                                dob.day
                            )

                        except ValueError:

                            next_birthday = date(
                                next_birthday_year,
                                2,
                                28
                            )


                    days_until_birthday = (
                        next_birthday - today
                    ).days


                    result = {

                        "years":
                            years,

                        "months":
                            months,

                        "days":
                            days,

                        "total_days":
                            total_days,

                        "next_birthday":
                            next_birthday.strftime(
                                "%d %B %Y"
                            ),

                        "days_until_birthday":
                            days_until_birthday
                    }


            except (ValueError, TypeError):

                error = (
                    "Please enter a valid date."
                )


    return render_template(
        "age_calculator.html",
        result=result,
        error=error,
        today=today.isoformat()
    )


# =========================
# PERCENTAGE CALCULATOR
# =========================

@app.route(
    "/calculator/percentage",
    methods=["GET", "POST"]
)
def percentage_calculator():

    result = None
    error = None


    if request.method == "POST":

        try:

            calculation_type = (
                request.form.get(
                    "calculation_type"
                )
            )


            number1 = float(
                request.form.get(
                    "number1",
                    0
                )
            )


            number2 = float(
                request.form.get(
                    "number2",
                    0
                )
            )


            if calculation_type == "percentage_of":

                value = (
                    number1 / 100
                ) * number2


                result = {

                    "title":
                        f"{number1:g}% of {number2:g}",

                    "value":
                        value
                }


            elif calculation_type == "what_percent":

                if number2 == 0:

                    error = (
                        "The second number cannot be zero."
                    )

                else:

                    value = (
                        number1 / number2
                    ) * 100


                    result = {

                        "title":
                            f"{number1:g} is what % of {number2:g}?",

                        "value":
                            value
                    }


            elif calculation_type == "increase":

                if number1 == 0:

                    error = (
                        "The original value cannot be zero."
                    )

                else:

                    value = (
                        (number2 - number1)
                        / number1
                    ) * 100


                    result = {

                        "title":
                            f"Increase from {number1:g} to {number2:g}",

                        "value":
                            value
                    }


            elif calculation_type == "decrease":

                if number1 == 0:

                    error = (
                        "The original value cannot be zero."
                    )

                else:

                    value = (
                        (number1 - number2)
                        / number1
                    ) * 100


                    result = {

                        "title":
                            f"Decrease from {number1:g} to {number2:g}",

                        "value":
                            value
                    }


            elif calculation_type == "marks":

                if number2 == 0:

                    error = (
                        "Total marks cannot be zero."
                    )

                else:

                    value = (
                        number1 / number2
                    ) * 100


                    result = {

                        "title":
                            f"{number1:g} out of {number2:g}",

                        "value":
                            value
                    }


        except (ValueError, TypeError):

            error = (
                "Please enter valid numbers."
            )


    return render_template(
        "percentage_calculator.html",
        result=result,
        error=error
    )


# =========================
# BMI CALCULATOR
# =========================

@app.route(
    "/calculator/bmi",
    methods=["GET", "POST"]
)
def bmi_calculator():

    result = None
    error = None


    if request.method == "POST":

        try:

            weight = float(
                request.form.get(
                    "weight",
                    0
                )
            )


            height = float(
                request.form.get(
                    "height",
                    0
                )
            )


            if weight <= 0 or height <= 0:

                error = (
                    "Please enter valid height and weight."
                )


            else:

                height_meters = (
                    height / 100
                )


                bmi = (
                    weight /
                    (height_meters ** 2)
                )


                if bmi < 18.5:

                    category = "Underweight"

                elif bmi < 25:

                    category = "Normal Weight"

                elif bmi < 30:

                    category = "Overweight"

                else:

                    category = "Obesity"


                result = {

                    "bmi":
                        round(bmi, 2),

                    "category":
                        category,

                    "weight":
                        weight,

                    "height":
                        height
                }


        except (ValueError, TypeError):

            error = (
                "Please enter valid numbers."
            )


    return render_template(
        "bmi_calculator.html",
        result=result,
        error=error
    )


# =========================
# DISCOUNT CALCULATOR
# =========================

@app.route(
    "/calculator/discount",
    methods=["GET", "POST"]
)
def discount_calculator():

    result = None
    error = None


    if request.method == "POST":

        try:

            original_price = float(
                request.form.get(
                    "original_price",
                    0
                )
            )


            discount_percent = float(
                request.form.get(
                    "discount_percent",
                    0
                )
            )


            if original_price < 0:

                error = (
                    "Original price cannot be negative."
                )


            elif (
                discount_percent < 0
                or discount_percent > 100
            ):

                error = (
                    "Discount must be between 0% and 100%."
                )


            else:

                discount_amount = (
                    original_price
                    * discount_percent
                    / 100
                )


                final_price = (
                    original_price
                    - discount_amount
                )


                result = {

                    "original_price":
                        original_price,

                    "discount_percent":
                        discount_percent,

                    "discount_amount":
                        discount_amount,

                    "final_price":
                        final_price
                }


        except (ValueError, TypeError):

            error = (
                "Please enter valid numbers."
            )


    return render_template(
        "discount_calculator.html",
        result=result,
        error=error
    )


# =========================
# LOAN / EMI CALCULATOR
# =========================

@app.route(
    "/calculator/emi",
    methods=["GET", "POST"]
)
def emi_calculator():

    result = None
    error = None


    if request.method == "POST":

        try:

            loan_amount = float(
                request.form.get(
                    "loan_amount",
                    0
                )
            )


            annual_rate = float(
                request.form.get(
                    "annual_rate",
                    0
                )
            )


            tenure_years = float(
                request.form.get(
                    "tenure_years",
                    0
                )
            )


            if loan_amount <= 0:

                error = (
                    "Loan amount must be greater than zero."
                )


            elif annual_rate < 0:

                error = (
                    "Interest rate cannot be negative."
                )


            elif tenure_years <= 0:

                error = (
                    "Loan tenure must be greater than zero."
                )


            else:

                monthly_rate = (
                    annual_rate / 12 / 100
                )


                months = round(
                    tenure_years * 12
                )


                if monthly_rate == 0:

                    emi = (
                        loan_amount / months
                    )


                else:

                    emi = (

                        loan_amount
                        * monthly_rate
                        * (1 + monthly_rate) ** months

                        /

                        (
                            (1 + monthly_rate) ** months
                            - 1
                        )

                    )


                total_payment = (
                    emi * months
                )


                total_interest = (
                    total_payment -
                    loan_amount
                )


                result = {

                    "loan_amount":
                        loan_amount,

                    "annual_rate":
                        annual_rate,

                    "tenure_years":
                        tenure_years,

                    "months":
                        months,

                    "emi":
                        emi,

                    "total_interest":
                        total_interest,

                    "total_payment":
                        total_payment
                }


        except (ValueError, TypeError):

            error = (
                "Please enter valid numbers."
            )


    return render_template(
        "emi_calculator.html",
        result=result,
        error=error
    )


# =========================
# GST CALCULATOR
# =========================

@app.route(
    "/calculator/gst",
    methods=["GET", "POST"]
)
def gst_calculator():

    result = None
    error = None


    if request.method == "POST":

        try:

            amount = float(
                request.form.get(
                    "amount",
                    0
                )
            )


            gst_rate = float(
                request.form.get(
                    "gst_rate",
                    0
                )
            )


            calculation_type = (
                request.form.get(
                    "calculation_type"
                )
            )


            if amount < 0:

                error = (
                    "Amount cannot be negative."
                )


            elif gst_rate < 0:

                error = (
                    "GST rate cannot be negative."
                )


            elif gst_rate > 100:

                error = (
                    "GST rate cannot be more than 100%."
                )


            elif calculation_type == "add":

                gst_amount = (
                    amount
                    * gst_rate
                    / 100
                )


                final_amount = (
                    amount +
                    gst_amount
                )


                result = {

                    "type":
                        "GST Added",

                    "base_amount":
                        amount,

                    "gst_rate":
                        gst_rate,

                    "gst_amount":
                        gst_amount,

                    "final_amount":
                        final_amount
                }


            elif calculation_type == "remove":

                if gst_rate == 0:

                    error = (
                        "GST rate must be greater than 0 "
                        "when removing GST."
                    )


                else:

                    base_amount = (
                        amount /
                        (1 + gst_rate / 100)
                    )


                    gst_amount = (
                        amount -
                        base_amount
                    )


                    result = {

                        "type":
                            "GST Removed",

                        "base_amount":
                            base_amount,

                        "gst_rate":
                            gst_rate,

                        "gst_amount":
                            gst_amount,

                        "final_amount":
                            amount
                    }


            else:

                error = (
                    "Please select a calculation type."
                )


        except (ValueError, TypeError):

            error = (
                "Please enter valid numbers."
            )


    return render_template(
        "gst_calculator.html",
        result=result,
        error=error
    )

# ==================================================
# QR CODE GENERATOR
# ==================================================

@app.route(
    "/qr-generator",
    methods=["GET", "POST"]
)
def qr_generator():

    qr_data = None
    error = None

    if request.method == "POST":

        text = request.form.get(
            "text",
            ""
        ).strip()

        if not text:

            error = (
                "Please enter a link or text."
            )

        else:

            try:

                qr = qrcode.QRCode(
                    version=None,
                    error_correction=qrcode.constants.ERROR_CORRECT_M,
                    box_size=10,
                    border=4
                )

                qr.add_data(text)

                qr.make(
                    fit=True
                )

                image = qr.make_image(
                    fill_color="black",
                    back_color="white"
                )

                output_filename = (
                    uuid.uuid4().hex
                    + ".png"
                )

                output_path = os.path.join(
                    app.config["REMOVED_FOLDER"],
                    output_filename
                )

                image.save(
                    output_path
                )

                qr_data = {

                    "text": text,

                    "image":
                        "/download/"
                        + output_filename

                }

            except Exception as e:

                print(
                    "QR generator error:",
                    e
                )

                error = (
                    "QR code could not be generated. "
                    "Please try again."
                )

    return render_template(
        "qr_generator.html",
        qr_data=qr_data,
        error=error
    )
@app.route("/pdf-merge", methods=["GET", "POST"])
def pdf_merge():
    error = None
    merged_file = None

    if request.method == "POST":

        files = request.files.getlist("pdfs")

        if not files or len(files) < 2:
            error = "Please select at least 2 PDF files."

        else:
            try:
                from pypdf import PdfWriter

                writer = PdfWriter()

                for pdf_file in files:

                    if pdf_file.filename == "":
                        continue

                    if not pdf_file.filename.lower().endswith(".pdf"):
                        continue

                    from io import BytesIO

                    pdf_data = pdf_file.read()

                    writer.append(BytesIO(pdf_data))

                if len(writer.pages) == 0:
                    error = "No valid PDF files selected."

                else:
                    output_filename = uuid.uuid4().hex + "_merged.pdf"

                    output_path = os.path.join(
                        app.config["REMOVED_FOLDER"],
                        output_filename
                    )

                    with open(output_path, "wb") as output_file:
                        writer.write(output_file)

                    merged_file = "/download/" + output_filename

            except Exception as e:
                print("PDF merge error:", e)
                error = "PDF files could not be merged."

    return render_template(
        "pdf_merge.html",
        error=error,
        merged_file=merged_file
    )
@app.route("/image-to-pdf", methods=["GET", "POST"])
def image_to_pdf():
    error = None
    pdf_file = None

    if request.method == "POST":

        image_files = request.files.getlist("images")

        # At least one image required
        if not image_files:
            error = "Please select at least one image."

        else:
            try:
                from PIL import Image
                from io import BytesIO

                images = []

                for image_file in image_files:

                    # Skip empty files
                    if image_file.filename == "":
                        continue

                    filename = image_file.filename.lower()

                    # Allow only image files
                    if not filename.endswith(
                        (".jpg", ".jpeg", ".png", ".webp")
                    ):
                        continue

                    image_data = image_file.read()

                    if not image_data:
                        continue

                    # Open image
                    image = Image.open(BytesIO(image_data))

                    # Convert image to RGB
                    # This is important for PNG/WebP images
                    if image.mode in ("RGBA", "LA", "P"):
                        background = Image.new(
                            "RGB",
                            image.size,
                            "white"
                        )

                        if image.mode == "P":
                            image = image.convert("RGBA")

                        background.paste(
                            image,
                            mask=image.getchannel("A")
                            if image.mode == "RGBA"
                            else None
                        )

                        image = background

                    else:
                        image = image.convert("RGB")

                    images.append(image)

                # Check whether valid images were found
                if len(images) == 0:

                    error = "No valid image files selected."

                else:

                    # Generate unique PDF filename
                    output_filename = (
                        uuid.uuid4().hex + "_images.pdf"
                    )

                    output_path = os.path.join(
                        app.config["REMOVED_FOLDER"],
                        output_filename
                    )

                    # First image + remaining images
                    first_image = images[0]
                    remaining_images = images[1:]

                    first_image.save(
                        output_path,
                        "PDF",
                        resolution=100.0,
                        save_all=True,
                        append_images=remaining_images
                    )

                    pdf_file = "/download/" + output_filename

            except Exception as e:

                print("Image to PDF error:", e)

                error = (
                    "Images could not be converted to PDF."
                )

    return render_template(
        "image_to_pdf.html",
        error=error,
        pdf_file=pdf_file
    )

# ==================================================
# IMAGE COMPRESSOR
# ==================================================

@app.route("/image-compressor", methods=["GET", "POST"])
def image_compressor():
    error = None
    compressed_file = None
    original_size = None
    compressed_size = None
    savings = None
    quality = 75

    if request.method == "POST":
        image_file = request.files.get("image")

        try:
            quality = int(request.form.get("quality", 75))
        except (ValueError, TypeError):
            quality = 75

        quality = max(20, min(95, quality))

        if image_file is None or image_file.filename == "":
            error = "Please select an image."

        elif not allowed_file(image_file.filename):
            error = "Only JPG, JPEG, PNG and WEBP images are allowed."

        else:
            try:
                from PIL import Image, ImageOps
                from io import BytesIO

                image_data = image_file.read()

                if not image_data:
                    error = "The selected image is empty."

                else:
                    original_size = len(image_data)

                    with Image.open(BytesIO(image_data)) as source_image:
                        image = ImageOps.exif_transpose(source_image)
                        image.load()

                        extension = image_file.filename.rsplit(".", 1)[1].lower()
                        output_extension = extension
                        output_format = {
                            "jpg": "JPEG",
                            "jpeg": "JPEG",
                            "png": "PNG",
                            "webp": "WEBP"
                        }[extension]

                        if output_format == "JPEG":
                            if image.mode in ("RGBA", "LA", "P"):
                                image = image.convert("RGBA")
                                background = Image.new("RGB", image.size, "white")
                                background.paste(image, mask=image.getchannel("A"))
                                image = background
                            else:
                                image = image.convert("RGB")

                        output_filename = uuid.uuid4().hex + "_compressed." + output_extension
                        output_path = os.path.join(app.config["REMOVED_FOLDER"], output_filename)

                        if output_format == "JPEG":
                            image.save(output_path, "JPEG", quality=quality, optimize=True, progressive=True)
                        elif output_format == "WEBP":
                            if image.mode not in ("RGB", "RGBA"):
                                image = image.convert("RGBA")
                            image.save(output_path, "WEBP", quality=quality, method=6)
                        else:
                            compress_level = round((100 - quality) / 100 * 9)
                            compress_level = max(0, min(9, compress_level))
                            image.save(output_path, "PNG", optimize=True, compress_level=compress_level)

                    compressed_size = os.path.getsize(output_path)

                    if original_size > 0:
                        savings = round((1 - (compressed_size / original_size)) * 100, 2)

                    compressed_file = "/download/" + output_filename

            except Exception as e:
                print("Image compressor error:", e)
                error = "Image could not be compressed. Please try another image."

    return render_template(
        "image_compressor.html",
        error=error,
        compressed_file=compressed_file,
        original_size=original_size,
        compressed_size=compressed_size,
        savings=savings,
        quality=quality
    )
# ==================================================
# IMAGE RESIZER - TARGET SIZE
# ==================================================

@app.route("/image-resizer", methods=["GET", "POST"])
def image_resizer():

    error = None
    resized_file = None

    original_size = None
    final_size = None
    target_bytes = None
    savings = None

    target_size = ""
    target_unit = "KB"

    def format_size(size_bytes):

        if size_bytes is None:
            return ""

        if size_bytes < 1024:
            return f"{size_bytes} B"

        if size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.2f} KB"

        return f"{size_bytes / (1024 * 1024):.2f} MB"


    def encode_image(image, quality, scale):

        from io import BytesIO
        from PIL import Image

        work_image = image.copy()

        # Resize dimensions if required
        if scale < 1:

            new_width = max(
                1,
                int(image.width * scale)
            )

            new_height = max(
                1,
                int(image.height * scale)
            )

            work_image = work_image.resize(
                (new_width, new_height),
                Image.Resampling.LANCZOS
            )


        # Convert to RGB for JPEG
        if work_image.mode != "RGB":

            if work_image.mode in (
                "RGBA",
                "LA",
                "P"
            ):

                if work_image.mode == "P":

                    work_image = work_image.convert(
                        "RGBA"
                    )

                if work_image.mode in (
                    "RGBA",
                    "LA"
                ):

                    background = Image.new(
                        "RGB",
                        work_image.size,
                        "white"
                    )

                    if work_image.mode == "LA":

                        alpha = work_image.getchannel(
                            "A"
                        )

                        work_image = work_image.convert(
                            "L"
                        )

                        background.paste(
                            work_image,
                            mask=alpha
                        )

                    else:

                        background.paste(
                            work_image,
                            mask=work_image.getchannel(
                                "A"
                            )
                        )

                    work_image = background

            else:

                work_image = work_image.convert(
                    "RGB"
                )


        output = BytesIO()

        work_image.save(
            output,
            format="JPEG",
            quality=quality,
            optimize=True,
            progressive=True
        )

        return output.getvalue()


    if request.method == "POST":

        image_file = request.files.get("image")

        target_size = request.form.get(
            "target_size",
            ""
        ).strip()

        target_unit = request.form.get(
            "target_unit",
            "KB"
        ).upper()


        # -----------------------------
        # Validate image
        # -----------------------------

        if image_file is None or image_file.filename == "":

            error = "Please select an image."


        elif not allowed_file(image_file.filename):

            error = (
                "Only JPG, JPEG, PNG and WEBP "
                "images are allowed."
            )


        else:

            try:

                target_number = float(
                    target_size
                )


                if target_number <= 0:

                    error = (
                        "Please enter a valid "
                        "target size."
                    )

                else:

                    # -----------------------------
                    # Convert target to bytes
                    # -----------------------------

                    if target_unit == "MB":

                        target_bytes = int(
                            target_number
                            * 1024
                            * 1024
                        )

                    else:

                        target_bytes = int(
                            target_number
                            * 1024
                        )


                    image_data = image_file.read()

                    if not image_data:

                        error = (
                            "The selected image "
                            "is empty."
                        )

                    else:

                        original_size = len(
                            image_data
                        )


                        # Target cannot be larger
                        if target_bytes >= original_size:

                            error = (
                                "Target size must be "
                                "smaller than the "
                                "original image."
                            )

                        else:

                            from PIL import Image, ImageOps
                            from io import BytesIO

                            with Image.open(
                                BytesIO(image_data)
                            ) as source_image:

                                image = ImageOps.exif_transpose(
                                    source_image
                                )

                                image.load()


                                # ---------------------------------
                                # First try original dimensions
                                # ---------------------------------

                                best_data = None

                                low_quality = 10
                                high_quality = 95


                                # Binary search quality
                                for _ in range(8):

                                    quality = (
                                        low_quality
                                        + high_quality
                                    ) // 2


                                    data = encode_image(
                                        image,
                                        quality,
                                        1.0
                                    )


                                    if len(data) <= target_bytes:

                                        best_data = data

                                        low_quality = (
                                            quality + 1
                                        )

                                    else:

                                        high_quality = (
                                            quality - 1
                                        )


                                # ---------------------------------
                                # If target is very small,
                                # reduce dimensions too
                                # ---------------------------------

                                if best_data is None:

                                    scale = 0.95

                                    while (
                                        scale >= 0.05
                                    ):

                                        data = encode_image(
                                            image,
                                            10,
                                            scale
                                        )


                                        if len(data) <= target_bytes:

                                            best_data = data

                                            # Improve quality
                                            # at this scale
                                            low_quality = 10
                                            high_quality = 95

                                            quality_best = 10

                                            for _ in range(8):

                                                quality = (
                                                    low_quality
                                                    + high_quality
                                                ) // 2

                                                test_data = encode_image(
                                                    image,
                                                    quality,
                                                    scale
                                                )


                                                if (
                                                    len(test_data)
                                                    <= target_bytes
                                                ):

                                                    best_data = test_data

                                                    quality_best = quality

                                                    low_quality = (
                                                        quality + 1
                                                    )

                                                else:

                                                    high_quality = (
                                                        quality - 1
                                                    )

                                            break


                                        scale -= 0.05


                                # ---------------------------------
                                # Final fallback
                                # ---------------------------------

                                if best_data is None:

                                    # Make the image very small
                                    scale = 0.05

                                    best_data = encode_image(
                                        image,
                                        10,
                                        scale
                                    )


                                # ---------------------------------
                                # Save result
                                # ---------------------------------

                                output_filename = (
                                    uuid.uuid4().hex
                                    + "_resized.jpg"
                                )


                                output_path = os.path.join(
                                    app.config[
                                        "REMOVED_FOLDER"
                                    ],
                                    output_filename
                                )


                                with open(
                                    output_path,
                                    "wb"
                                ) as output_file:

                                    output_file.write(
                                        best_data
                                    )


                                final_size = os.path.getsize(
                                    output_path
                                )


                                savings = round(
                                    (
                                        1
                                        - (
                                            final_size
                                            / original_size
                                        )
                                    )
                                    * 100,
                                    2
                                )


                                resized_file = (
                                    "/download/"
                                    + output_filename
                                )


            except Exception as e:

                print(
                    "Image resizer error:",
                    e
                )

                error = (
                    "Image could not be resized. "
                    "Please try another image."
                )


    return render_template(
        "image_resizer.html",

        error=error,

        resized_file=resized_file,

        original_size=original_size,

        final_size=final_size,

        target_bytes=target_bytes,

        savings=savings,

        target_size=target_size,

        target_unit=target_unit,

        format_size=format_size
    )

# ==================================================
# BACKGROUND REMOVER
# ==================================================

@app.route(
    "/background-remover",
    methods=["GET", "POST"]
)
def background_remover():

    if request.method == "GET":
        return render_template("background_remover.html")

    if "image" not in request.files:
        return {"error": "Please select an image."}, 400

    file = request.files["image"]

    if file.filename == "":
        return {"error": "Please select an image."}, 400

    if not allowed_file(file.filename):
        return {
            "error": "Only PNG, JPG, JPEG and WEBP images are allowed."
        }, 400

    input_filename = secure_filename(file.filename)
    input_path = os.path.join(
        app.config["UPLOAD_FOLDER"],
        uuid.uuid4().hex + "_" + input_filename
    )

    output_filename = uuid.uuid4().hex + ".png"
    output_path = os.path.join(
        app.config["REMOVED_FOLDER"],
        output_filename
    )

    try:
        file.save(input_path)

        with open(input_path, "rb") as input_file:
            input_data = input_file.read()

        output_data = remove(input_data, session=REMBG_SESSION)

        with open(output_path, "wb") as output_file:
            output_file.write(output_data)

        with open(output_path, "rb") as output_file:
            result_b64 = base64.b64encode(
                output_file.read()
            ).decode("ascii")

        try:
            os.remove(input_path)
        except OSError:
            pass

        return {
            "result": "data:image/png;base64," + result_b64,
            "download": "/download/" + output_filename
        }

    except Exception as e:
        print("Background remover error:", e)

        try:
            if os.path.exists(input_path):
                os.remove(input_path)
        except OSError:
            pass

        try:
            if os.path.exists(output_path):
                os.remove(output_path)
        except OSError:
            pass

        return {
            "error": "Background removal failed. Please try another image."
        }, 500


# =========================
# DOWNLOAD REMOVED IMAGE
# =========================

@app.route(
    "/download/<filename>"
)
def download_image(filename):

    return send_from_directory(
        app.config["REMOVED_FOLDER"],
        filename,
        as_attachment=True
    )


# =========================
# RUN APPLICATION
# =========================

if __name__ == "__main__":

    app.run(
        debug=True
    )