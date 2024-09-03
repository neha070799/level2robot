from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive
import os
import glob





@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    browser.configure(
        slowmo=100,
    )
    orders = get_orders()
    open_robot_order_website()
    close_annoying_modal()
    fill_the_form(orders)
    archive_receipts()

def open_robot_order_website():
    browser.goto("https://robotsparebinindustries.com/#/robot-order")
    
def get_orders():
    """Downloads CSV file from the given URL"""
    http = HTTP()
    http.download(url="https://robotsparebinindustries.com/orders.csv", overwrite=True)
    
    """Read data from CSV and save as a table"""
    library = Tables()
    orders = library.read_table_from_csv("orders.csv", columns=["Order number","Head","Body","Legs","Address"])
    return orders

def close_annoying_modal():
    """Closes the annoying modal that pops up"""
    page = browser.page()
    page.click("button:text('OK')")

def fill_the_form(orders):
    for row in orders:
        page = browser.page()
        page.select_option("#head", row["Head"])
        id='#id-body-'+str(row["Body"])
        page.click(id)
        page.fill("//html/body/div/div/div[1]/div/div[1]/form/div[3]/input", row["Legs"])
        page.fill("#address", row["Address"])
        page.click("button:text('Preview')")
        # page.click("button:text('Order')") # Add your code here
        while True:
            page.click("#order")
            order_another = page.query_selector("#order-another")
            if order_another:
                pdf_path = store_receipt_as_pdf(row["Order number"])
                screenshot_path = screenshot_robot(row["Order number"])
                embed_screenshot_to_receipt(screenshot_path, pdf_path)
                page.click("#order-another")
                page.click('text=OK')
                break
        
def store_receipt_as_pdf(order_number):
    """Export the data to a pdf file"""
    page = browser.page()
    receipt_html = page.locator("#receipt").inner_html()
    pdf = PDF()
    name = "output/receipt_" + order_number + ".pdf"
    pdf.html_to_pdf(receipt_html, name)
    return name

def screenshot_robot(order_number):
    """Take a screenshot of the page"""
    page = browser.page()
    name = "output/robot_" + order_number + ".png"
    page.locator("#robot-preview-image").screenshot(path=name)
    return name

def embed_screenshot_to_receipt(screenshot_path, pdf_path):
    """Embeds the screenshot to the PDF receipt"""
    pdf = PDF()
    pdf.add_watermark_image_to_pdf(image_path=screenshot_path, source_path=pdf_path, output_path=pdf_path)

def archive_receipts():
    lib = Archive()
    lib.archive_folder_with_zip('./output', './output/zip_receipts.zip', include='*.pdf')
    files_pdf = glob.glob('./output/*.pdf')
    files_png = glob.glob('./output/*.png')
    for file in files_pdf:
        os.remove(file)
    for file in files_png:
        os.remove(file)
