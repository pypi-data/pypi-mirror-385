import pandas as pd
from influxdb import DataFrameClient
import json
import base64
import qrcode
from IPython.display import Image


#print("Cozie Module start")
class CozieQR:
  """
  Class to retrieve and process Cozie-Apple data
  """

  def __init__(self):   
    """
    Constructor initializes class attributes and prints test string
    
    Arguments
    ----------
      -
    
    Returns
    -------
      -
    """
    self.test_string = 'CoziePy Test String'
    self.deep_link_url = ""
    self.payload = {}
    self.payload["id_participant"] = "test_participant"
    self.payload["id_experiment"] = "test_experiment"
    self.payload["wss_title"] = "Thermal (long)"
    self.payload["wss_goal"] = 150
    self.payload["wss_time_out"] = 3500
    self.payload["wss_reminder_enabeled"] = True
    self.payload["wss_participation_time_start"] = "09:00"
    self.payload["wss_participation_time_end"] = "18:00"
    self.payload["wss_participation_days"] = "Mo,Tu,We,Th"
    self.payload["wss_reminder_interval"] = 60
    self.payload["pss_reminder_enabled"] = True
    self.payload["pss_reminder_days"] = "Fr"
    self.payload["pss_reminder_time"] = "14:00"
    self.payload["api_read_url"] = "https://d3lupjxfs7.execute-api.ap-southeast-1.amazonaws.com/prod/read-influx"
    self.payload["api_read_key"] = "XsM7ks4lLU3JexCO8RjHG6nKq8yj9oBJ7bdI3R3R"
    self.payload["api_write_url"] = "https://d3lupjxfs7.execute-api.ap-southeast-1.amazonaws.com/prod/write-queue"
    self.payload["api_write_key"] = "XsM7ks4lLU3JexCO8RjHG6nKq8yj9oBJ7bdI3R3R"
    self.payload["app_one_signal_app_id"] = "be00093b-ed75-4c2e-81af-d6b382587283"
    self.payload["id_password"] = "test_password"
    self.payload["api_watch_survey_url"] = "https://www.cozie-apple.app/watch_surveys/watch_survey_example.json"
    self.payload["api_phone_survey_url"] = "https://docs.google.com/forms/d/e/1FAIpQLSfOj7_vVRUNDHELmwQqvpFYF5m1p6IXpXaWsQgHOF8HxuTmrw/viewform"

  def test(self):    
    """
    Function for testing, prints test string
    
    Arguments
    ----------
      -   
    
    Returns
    -------
      - test_string, str, String for testing
    """
    print("test")
    print(self.test_string)
    return self.test_string

  def set(self, parameter={}):    
    """
    Function to set parameters in QR code
    
    Arguments
    ----------
      -   
    
    Returns
    -------
      - 
    """
    for key in parameter:
      if key in self.payload:
        self.payload[key] = parameter[key]
      else:
        print(f'"{key}" is not a valid key')

  def create(self):    
    """
    Function to create QR code
    
    Arguments
    ----------
      - None 
    
    Returns
    -------
      - test_string, str, String for testing
    """
    
    payload = self.payload

    # Convert dictionary to string
    payload = json.dumps(payload)

    # Convert payload to deep link
    payload_bytes = payload.encode("ascii")
    base64_bytes = base64.b64encode(payload_bytes)
    base64_payload = base64_bytes.decode("ascii")
    deep_link_url = "cozie://param?data=" + base64_payload

    # Print deep link
    print(deep_link_url)
    print(
        "Number of characters:",
        len(deep_link_url),
        "of 2048 characters (",
        int(len(deep_link_url) / 2048 * 100),
        "%)",
    )

    # Generate QR code
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(deep_link_url)
    qr.make(fit=True)
    img = qr.make_image(fill="black", back_color="white")
    img.save("qrcode001.png")
    Image("qrcode001.png", width=700, height=700)

    return deep_link_url 