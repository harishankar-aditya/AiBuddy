import os
import logging
import smtplib

import uuid

from datetime import datetime

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from database.PostgresConnection import DatabaseConnection
# from api.authorization.otp.OtpEmailTemplate import EmailTemplate
from dotenv import load_dotenv
load_dotenv()


# Connect to the EMAIL server
mailserver = smtplib.SMTP_SSL('smtpout.secureserver.net', 465)
mailserver.ehlo()  # Say hello to the server
sender_email = os.getenv("adminEmail", "")
password = os.getenv("adminPassword", "")
mailserver.login(sender_email, password)


def fetch_user_data(DB_conn, email):
    query_dict = f"SELECT user_id, username, email FROM users WHERE email = '{email}' AND is_user_active = true"
    result = DB_conn.execute_query(query_dict)
    return result

def insert_in_db(username, email, otp, request_id):
    DB_conn = DatabaseConnection()
    user_data = fetch_user_data(DB_conn, email)
    current_time = datetime.now()
    if user_data:
        user_id = user_data[0]['user_id']
        expire_otp_query = {
                            "query": "UPDATE login_token SET is_otp_active = %s, updated_at = %s WHERE user_id = %s",
                            "data": ('false', current_time, user_id)
                        }
                    
        token_query = {
                            "query": "INSERT INTO login_token (user_id, email, otp, request_id) VALUES (%s, %s, %s, %s)",
                            "data": (user_id, email, otp, request_id)
                        }
                    
        response = DB_conn.insert_user_data([expire_otp_query, token_query])

        # user_query = {
        #                     "query": "UPDATE users SET username = %s, updated_at = %s, last_login_at = %s WHERE user_id = %s",
        #                     "data": (username, current_time, current_time, user_id)
        #                 }
            
        # response = DB_conn.insert_user_data([expire_otp_query, token_query, user_query])
    else:
        user_id = str(uuid.uuid4())
        create_user_query = {
                            "query": "INSERT INTO users (user_id, username, email) VALUES (%s, %s, %s)",
                            "data": (user_id, username, email)
                        }
                    
        token_query = {
                            "query": "INSERT INTO login_token (user_id, email, otp, request_id) VALUES (%s, %s, %s, %s)",
                            "data": (user_id, email, otp, request_id)
                        }
        
        response = DB_conn.insert_user_data([create_user_query, token_query])

    return response

def send_otp_to_email(username, email: str, otp: str, request_id: str):
    """
    Sends an OTP to the specified email address.
    """
    try:
        response = {
            "status_code": 400,
            "message": "Invalid Email!"
        }

        sender_email = os.getenv("adminEmail", "")
        receiver_email = email
        # password = os.getenv("adminPassword", "")

        msg = MIMEMultipart()

        msg.set_unixfrom('author')

        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = 'Login OTP for Sophius Buddy'
        # message = f'Your OTP to login to Sophius Buddy is {otp}.'
        # msg.attach(MIMEText(message))
        # message = f"{EmailTemplate}"
        # message = EmailTemplate % (username, otp)
        message = f'''
                <div class="">
                <div class="aHl"></div>
                <div id=":24" tabindex="-1"></div>
                <div id=":1u" class="ii gt"
                    jslog="20277; u014N:xr6bB; 1:WyIjdGhyZWFkLWY6MTcxOTA2ODE5NDI0NDQ2NzU1MCJd; 4:WyIjbXNnLWY6MTcxOTA2ODE5NDI0NDQ2NzU1MCIsbnVsbCxudWxsLG51bGwsMSwwLFsxLDAsMF0sMTY0LDk1MixudWxsLG51bGwsbnVsbCxudWxsLG51bGwsMSxudWxsLG51bGwsWzNdLG51bGwsbnVsbCxudWxsLG51bGwsbnVsbCxudWxsLDBd">
                    <div id=":1t" class="a3s aiL msg8335595697985763314"><u></u><u></u>






                        <div
                            style="margin:0;Margin:0;padding:0;border:0;outline:0;width:100%;min-width:100%;height:100%;font-family:'Effra','Montserrat',Helvetica,Arial,sans-serif;line-height:24px;font-weight:normal;font-size:16px;box-sizing:border-box;background-color:#f8f9fa">
                            <table valign="top" border="0" cellpadding="0" cellspacing="0"
                                style="border-spacing:0px;border-collapse:collapse;margin:0;Margin:0;padding:0;border:0;outline:0;width:100%;min-width:100%;height:100%;font-family:'Effra','Montserrat',Helvetica,Arial,sans-serif;line-height:24px;font-weight:normal;font-size:16px;box-sizing:border-box"
                                width="100%" height="100%">
                                <tbody>
                                    <tr>
                                        <td valign="top"
                                            style="line-height:24px;font-size:16px;margin:0;border-spacing:0px;border-collapse:collapse">




                                            <table border="0" cellpadding="0" cellspacing="0"
                                                style="font-family:'Effra','Montserrat',Helvetica,Arial,sans-serif;border-spacing:0px;border-collapse:collapse;width:100%"
                                                width="100%">
                                                <tbody>
                                                    <tr>
                                                        <td align="center"
                                                            style="line-height:24px;font-size:16px;margin:0;border-spacing:0px;border-collapse:collapse">







                                                            <table
                                                                style="font-family:'Effra','Montserrat',Helvetica,Arial,sans-serif;border-spacing:0px;border-collapse:collapse;width:100%;max-width:630px;border:solid 1px #ddd;background-color:white;margin-top:24px;margin-bottom:24px"
                                                                border="0" cellpadding="0" cellspacing="0" width="100%"
                                                                bgcolor="white">
                                                                <tbody>
                                                                    <tr>
                                                                        <td align="left"
                                                                            style="line-height:24px;font-size:16px;margin:0;border-spacing:0px;border-collapse:collapse;width:100%;padding:0 15px;text-align:left"
                                                                            width="100%">



                                                                            <table border="0" cellpadding="0" cellspacing="0"
                                                                                style="font-family:'Effra','Montserrat',Helvetica,Arial,sans-serif;border-spacing:0px;border-collapse:collapse;width:100%;text-align:center"
                                                                                width="100%" align="center">
                                                                                <tbody>
                                                                                    <tr>
                                                                                        <td
                                                                                            style="line-height:24px;font-size:16px;margin:0;border-spacing:0px;border-collapse:collapse">
                                                                                            <!-- <img src="https://ci3.googleusercontent.com/meips/ADKq_NaPqEphmRvnXUY8UGCVS1c6NHyJGqvz_MvPlLkoadn3gGLOe90af6pD7U07cP7aEPo0KlcSgJPKvkwsEkv4-YquiGAWyudiNuy7Tz16Ev7kEf89-8j6O5GgHgmyQEyJ0y17Li6lGP0Gvg=s0-d-e1-ft#https://coindcx-public.s3.ap-south-1.amazonaws.com/logos/rebrand-coindcx-header.png" -->
                                                                                            <img src="https://aditya-birla-public-bucket.s3.ap-south-1.amazonaws.com/sophiusjpg.png"
                                                                                                style="border:0 none;height:100px;line-height:100%;outline:none;text-decoration:none;width:400;max-width:600px; margin-top: 15px;"
                                                                                                class="CToWUd a6T" data-bit="iit"
                                                                                                tabindex="0">
                                                                                            <div class="a6S" dir="ltr"
                                                                                                style="opacity: 0.01; left: 771.016px; top: 138px;">
                                                                                                <span data-is-tooltip-wrapper="true"
                                                                                                    class="a5q"
                                                                                                    jsaction="JIbuQc:.CLIENT"><button
                                                                                                        class="VYBDae-JX-I VYBDae-JX-I-ql-ay5-ays CgzRE"
                                                                                                        jscontroller="PIVayb"
                                                                                                        jsaction="click:h5M12e; clickmod:h5M12e;pointerdown:FEiYhc;pointerup:mF5Elf;pointerenter:EX0mI;pointerleave:vpvbp;pointercancel:xyn4sd;contextmenu:xexox;focus:h06R8; blur:zjh6rb;mlnRJb:fLiPzd;"
                                                                                                        data-idom-class="CgzRE"
                                                                                                        data-use-native-focus-logic="true"
                                                                                                        jsname="hRZeKc"
                                                                                                        aria-label="Download attachment "
                                                                                                        data-tooltip-enabled="true"
                                                                                                        data-tooltip-id="tt-c1"
                                                                                                        data-tooltip-classes="AZPksf"
                                                                                                        id=""
                                                                                                        jslog="91252; u014N:cOuCgd,Kr2w4b,xr6bB; 4:WyIjbXNnLWY6MTcxOTA2ODE5NDI0NDQ2NzU1MCJd; 43:WyJpbWFnZS9qcGVnIl0."><span
                                                                                                            class="OiePBf-zPjgPe VYBDae-JX-UHGRz"></span><span
                                                                                                            class="bHC-Q"
                                                                                                            jscontroller="LBaJxb"
                                                                                                            jsname="m9ZlFb"
                                                                                                            soy-skip=""
                                                                                                            ssk="6:RWVI5c"></span><span
                                                                                                            class="VYBDae-JX-ank-Rtc0Jf"
                                                                                                            jsname="S5tZuc"
                                                                                                            aria-hidden="true"><span
                                                                                                                class="notranslate bzc-ank"
                                                                                                                aria-hidden="true">
                                                                                                        <div class="VYBDae-JX-ano">
                                                                                                        </div>
                                                                                                    </button>
                                                                                                    <div class="ne2Ple-oshW8e-J9"
                                                                                                        id="tt-c1" role="tooltip"
                                                                                                        aria-hidden="true">Download
                                                                                                    </div>
                                                                                                </span>
                                                                                            </div>

                                                                                        </td>
                                                                                    </tr>
                                                                                </tbody>
                                                                            </table>

                                                                            <p
                                                                                style="line-height:24px;font-size:16px;margin:0;width:100%; color: #F68529;">

                                                                                <strong>Hi {username},</strong><br><br>


                                                                            </p>
                                                                            <p
                                                                                style="line-height:24px;font-size:16px;margin:0;width:100%">
                                                                            </p>
                                                                            Here’s Your Login OTP for Sophius Buddy:
                                                                            <strong style="color: #F68529;">{otp}</strong>. The OTP is valid for 10 minutes.<br><br>

                                                                            <p
                                                                                style="line-height:24px;font-size:16px;margin:0;width:100%">
                                                                            </p>

                                                                            This OTP will be used to verify the device. For account
                                                                            safety, do not share your OTP with others.<br><br>
                                                                            <p
                                                                                style="line-height:24px;font-size:16px;margin:0;width:100%">
                                                                            </p>
                                                                            <p
                                                                                style="line-height:24px;font-size:16px;margin:0;width:100%">
                                                                            </p>
                                                                            <p
                                                                                style="line-height:24px;font-size:16px;margin:0;width:100%">
                                                                            </p>
                                                                            <p
                                                                                style="line-height:24px;font-size:16px;margin:0;width:100%">
                                                                            </p>
                                                                            <p
                                                                                style="line-height:24px;font-size:16px;margin:0;width:100%">
                                                                            </p>
                                                                            <p
                                                                                style="line-height:24px;font-size:16px;margin:0;width:100%">
                                                                                Regards,<br>
                                                                                <strong>Team Sophius Buddy.</strong></p>
                                                                            <p
                                                                                style="line-height:24px;font-size:16px;margin:0;width:100%">
                                                                            </p>

                                                                            <table border="0" cellpadding="0" cellspacing="0"
                                                                                style="font-family:'Effra','Montserrat',Helvetica,Arial,sans-serif;border-spacing:0px;border-collapse:collapse;width:100%;border:0"
                                                                                width="100%">
                                                                                <tbody>
                                                                                    <tr>
                                                                                        <td style="line-height:24px;font-size:16px;margin:0;border-spacing:0px;border-collapse:collapse;width:100%;padding:16px 0"
                                                                                            width="100%">
                                                                                            <table border="0" cellpadding="0"
                                                                                                cellspacing="0"
                                                                                                style="font-family:'Effra','Montserrat',Helvetica,Arial,sans-serif;border-spacing:0px;border-collapse:collapse;width:100%"
                                                                                                width="100%">
                                                                                                <tbody>
                                                                                                    <tr>
                                                                                                        <td style="margin:0;border-spacing:0px;border-collapse:collapse;border-top:1px solid #adb5bd;height:1px;width:100%;font-size:0;line-height:0"
                                                                                                            width="100%" height="1">
                                                                                                            &nbsp;</td>
                                                                                                    </tr>
                                                                                                </tbody>
                                                                                            </table>
                                                                                        </td>
                                                                                    </tr>
                                                                                </tbody>
                                                                            </table>




                                                                            <table
                                                                                class="m_8335595697985763314bte-spacing-container m_8335595697985763314sb-4"
                                                                                border="0" cellpadding="0" cellspacing="0"
                                                                                style="font-family:'Effra','Montserrat',Helvetica,Arial,sans-serif;border-spacing:0px;border-collapse:collapse;table-layout:fixed;width:100%"
                                                                                width="100%">
                                                                                <tbody>
                                                                                    <tr>
                                                                                        <td class="m_8335595697985763314bte-space-top m_8335595697985763314bte-space-left"
                                                                                            style="margin:0;border-spacing:0px;border-collapse:collapse;width:0;line-height:0;height:0;font-size:0;padding:0">
                                                                                            &nbsp;</td>
                                                                                        <td class="m_8335595697985763314bte-space-top"
                                                                                            style="margin:0;border-spacing:0px;border-collapse:collapse;line-height:0;height:0;font-size:0;padding:0">
                                                                                            &nbsp;</td>
                                                                                        <td class="m_8335595697985763314bte-space-top m_8335595697985763314bte-space-right"
                                                                                            style="margin:0;border-spacing:0px;border-collapse:collapse;width:0;line-height:0;height:0;font-size:0;padding:0">
                                                                                            &nbsp;</td>
                                                                                    </tr>
                                                                                    <tr>
                                                                                        <td class="m_8335595697985763314bte-space-left"
                                                                                            style="margin:0;border-spacing:0px;border-collapse:collapse;width:0;line-height:0;height:0;font-size:0;padding:0">
                                                                                            &nbsp;</td>
                                                                                        <td
                                                                                            style="line-height:24px;font-size:16px;margin:0;border-spacing:0px;border-collapse:collapse">


                                                                                            <strong>
                                                                                                <div class="m_8335595697985763314blue"
                                                                                                    style="text-align:center">
                                                                                                    IMPORTANT</div>
                                                                                            </strong>
                                                                                            <div class="m_8335595697985763314blue"
                                                                                                style="margin-top:0;margin-bottom:0;font-weight:400;color:inherit;vertical-align:baseline;font-size:16px;line-height:20.8px;text-align:center">
                                                                                                Please do not reply to this email
                                                                                            </div>

                                                                                            <p
                                                                                                style="line-height:24px;font-size:16px;margin:0;width:100%">
                                                                                            </p>

                                                                                            <div class="m_8335595697985763314blue"
                                                                                                style="text-align:center">For any
                                                                                                queries</div>
                                                                                            <div class="m_8335595697985763314blue"
                                                                                                style="margin-top:0;margin-bottom:0;font-weight:400;color:inherit;vertical-align:baseline;font-size:16px;line-height:20.8px;text-align:center">
                                                                                                <!-- <a class="m_8335595697985763314orange"
                                                                                                    href="https://support.coindcx.com/hc/en-gb/requests/new"
                                                                                                    style="color:#1c2951;text-decoration:none;background-color:transparent"
                                                                                                    target="_blank"
                                                                                                    data-saferedirecturl="https://www.google.com/url?q=https://support.coindcx.com/hc/en-gb/requests/new&amp;source=gmail&amp;ust=1735662706774000&amp;usg=AOvVaw1JK3Yws-Sk3uLHvlqaH3AU">Raise
                                                                                                    a Support Ticket</a> | -->
                                                                                                <a class="m_8335595697985763314orange"
                                                                                                    href="https://x.com/AdityaBirlaGrp"
                                                                                                    style="color:#1c2951;text-decoration:none;background-color:transparent"
                                                                                                    target="_blank"
                                                                                                    data-saferedirecturl="https://www.google.com/url?q=https://x.com/AdityaBirlaGrp&amp;source=gmail&amp;ust=1735662706774000&amp;usg=AOvVaw0kMvrhqkFz01FOVjbYyxQ3">Reach
                                                                                                    us on Twitter</a>
                                                                                            </div>

                                                                                            <div class="m_8335595697985763314blue"
                                                                                                style="margin-bottom:0;font-weight:400;color:inherit;vertical-align:baseline;font-size:16px;line-height:20.8px;margin-top:10px;text-align:center">
                                                                                                <a href="https://x.com/AdityaBirlaGrp"
                                                                                                    style="color:#1c2951;text-decoration:none;background-color:transparent"
                                                                                                    target="_blank"
                                                                                                    data-saferedirecturl="https://www.google.com/url?q=https://x.com/AdityaBirlaGrp&amp;source=gmail&amp;ust=1735662706774000&amp;usg=AOvVaw0kMvrhqkFz01FOVjbYyxQ3">
                                                                                                    <img src="https://ci3.googleusercontent.com/meips/ADKq_NavIUYQT_wV66_Num5cZMmnGfcdQzFRj-MxA0rMqMdaDD5dTraiRqbe4AKBvqjf3c0bfqPHmY6SpVa4CNaeVp51oXLRP1lI-kZv0mBJ_aL9GW1VKhxCf14bz7_2OYbPXKCq=s0-d-e1-ft#https://coindcx-public.s3.ap-south-1.amazonaws.com/logos/coindcx-twitter.png"
                                                                                                        style="height:auto;line-height:100%;outline:none;text-decoration:none;border:0 none;width:32px;margin:10px"
                                                                                                        width="32" class="CToWUd"
                                                                                                        data-bit="iit">
                                                                                                </a>
                                                                                                <a href="https://www.youtube.com/channel/UC1DO0n9pB_LzCtEYQifPOZQ"
                                                                                                    style="color:#1c2951;text-decoration:none;background-color:transparent"
                                                                                                    target="_blank"
                                                                                                    data-saferedirecturl="https://www.google.com/url?q=https://www.youtube.com/channel/UC1DO0n9pB_LzCtEYQifPOZQ/&amp;source=gmail&amp;ust=1735662706774000&amp;usg=AOvVaw2axQU1IizvKFKmYCb_79aq">
                                                                                                    <img src="https://ci3.googleusercontent.com/meips/ADKq_NY6UkN6P5pKH2jH2ok6srt5Zao-RUKeMlBeXHxgbaWJHrlhPUZtHlWH7UIdBHzZx2lr27vslCbDjCarAHm6zmzP3hK_A8vngBaSSPLYbXPO7sryk-7mFCQWn9yMbydYTCbT=s0-d-e1-ft#https://coindcx-public.s3.ap-south-1.amazonaws.com/logos/coindcx-youtube.png"
                                                                                                        style="height:auto;line-height:100%;outline:none;text-decoration:none;border:0 none;width:32px;margin:10px"
                                                                                                        width="32" class="CToWUd"
                                                                                                        data-bit="iit">
                                                                                                </a>
                                                                                                <a href="https://t.me/adityabirlagrp/"
                                                                                                    style="color:#1c2951;text-decoration:none;background-color:transparent"
                                                                                                    target="_blank"
                                                                                                    data-saferedirecturl="https://www.google.com/url?q=https://t.me/coindcx/&amp;source=gmail&amp;ust=1735662706774000&amp;usg=AOvVaw0j80nsLkcFgME-HIG5dk41">
                                                                                                    <img src="https://ci3.googleusercontent.com/meips/ADKq_NbvqRuQi65SkhIw6mxXYTykY86lNGBUnaOgKU2xWSgTQMva4y573llKCAGMbIwNxoMi1nAMJeI1vYwHYVLaEeYFOt9cjS39CvxwpNfGhw8EBv11C0veeQUWje1xq0lV_lk2xg=s0-d-e1-ft#https://coindcx-public.s3.ap-south-1.amazonaws.com/logos/coindcx-telegram.png"
                                                                                                        style="height:auto;line-height:100%;outline:none;text-decoration:none;border:0 none;width:32px;margin:10px"
                                                                                                        width="32" class="CToWUd"
                                                                                                        data-bit="iit">
                                                                                                </a>
                                                                                            </div>

                                                                                            <p
                                                                                                style="line-height:24px;font-size:16px;margin:0;width:100%">
                                                                                            </p>

                                                                                            <p class="m_8335595697985763314small"
                                                                                                style="line-height:24px;margin:0;width:100%;font-size:12.8px;font-weight:400">
                                                                                                Please do not share your OTP,
                                                                                                Password or any sensitive
                                                                                                information with anyone.</p>

                                                                                            <p
                                                                                                style="line-height:24px;font-size:16px;margin:0;width:100%">
                                                                                            </p>

                                                                                            <div class="m_8335595697985763314small"
                                                                                                style="font-size:12.8px;font-weight:400">
                                                                                                <strong
                                                                                                    class="m_8335595697985763314blue">How
                                                                                                    do I know an email is from
                                                                                                    Sophius?</strong>
                                                                                            </div>
                                                                                            <div class="m_8335595697985763314small m_8335595697985763314blue"
                                                                                                style="font-size:12.8px;font-weight:400">
                                                                                                Links in this email will start with
                                                                                                "https://" and contain "<a
                                                                                                    href="http://hiara.live"
                                                                                                    target="_blank"
                                                                                                    data-saferedirecturl="https://www.google.com/url?q=http://hiara.live&amp;source=gmail&amp;ust=1735662706774000&amp;usg=AOvVaw0AbCuOV6pNJv7nrUV2Byky">hiara.live</a>".
                                                                                                Your browser will also display a
                                                                                                padlock icon to let you know a site
                                                                                                is secure.</div>

                                                                                            <p
                                                                                                style="line-height:24px;font-size:16px;margin:0;width:100%">
                                                                                            </p>

                                                                                            <div class="m_8335595697985763314small"
                                                                                                style="font-size:12.8px;font-weight:400">
                                                                                                <strong
                                                                                                    class="m_8335595697985763314blue">DISCLAIMER</strong>
                                                                                            </div>
                                                                                            <div class="m_8335595697985763314small m_8335595697985763314blue"
                                                                                                style="font-size:12.8px;font-weight:400">
                                                                                                This is the Beta version of Sophius Buddy, 
                                                                                                and as such, it may contain bugs or 
                                                                                                incomplete features. We appreciate your 
                                                                                                feedback to help us improve the platform. 
                                                                                                Please use it with discretion, and note 
                                                                                                that we are not liable for any issues arising 
                                                                                                from its use during this testing phase.</div>

                                                                                            <p
                                                                                                style="line-height:24px;font-size:16px;margin:0;width:100%">
                                                                                            </p>

                                                                                            <div class="m_8335595697985763314small m_8335595697985763314blue"
                                                                                                style="font-size:12.8px;font-weight:400">
                                                                                                © 2024-2025 Sophius. All rights
                                                                                                reserved.</div>
                                                                                            <div class="m_8335595697985763314small m_8335595697985763314blue"
                                                                                                style="font-size:12.8px;font-weight:400">
                                                                                                Office of Ananya Birla, 
                                                                                                17th Floor, BIRLA AURORA, <br>
                                                                                                Century Bazaar, Prabhadevi, 
                                                                                                Mumbai, Maharashtra 400025</div>


                                                                                        </td>
                                                                                        <td class="m_8335595697985763314bte-space-right"
                                                                                            style="margin:0;border-spacing:0px;border-collapse:collapse;width:0;line-height:0;height:0;font-size:0;padding:0">
                                                                                            &nbsp;</td>
                                                                                    </tr>
                                                                                    <tr>
                                                                                        <td class="m_8335595697985763314bte-space-bottom m_8335595697985763314bte-space-left"
                                                                                            style="margin:0;border-spacing:0px;border-collapse:collapse;width:0;line-height:24px;height:24px;font-size:0;padding:0"
                                                                                            height="24">&nbsp;</td>
                                                                                        <td class="m_8335595697985763314bte-space-bottom"
                                                                                            style="margin:0;border-spacing:0px;border-collapse:collapse;line-height:24px;height:24px;font-size:0;padding:0"
                                                                                            height="24">&nbsp;</td>
                                                                                        <td class="m_8335595697985763314bte-space-bottom m_8335595697985763314bte-space-right"
                                                                                            style="margin:0;border-spacing:0px;border-collapse:collapse;width:0;line-height:24px;height:24px;font-size:0;padding:0"
                                                                                            height="24">&nbsp;</td>
                                                                                    </tr>
                                                                                </tbody>
                                                                            </table>





                                                                        </td>
                                                                    </tr>
                                                                </tbody>
                                                            </table>








                                                        </td>
                                                    </tr>
                                                </tbody>
                                            </table>


                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                            <div class="yj6qo"></div>
                            <div class="adL">

                            </div>
                        </div>
                        <div class="adL">
                        </div>
                    </div>
                </div>
                <div class="WhmR8e" data-hash="0"></div>
            </div>
                '''
        msg.attach(MIMEText(message, 'html'))

        # Connect to the server
        # mailserver = smtplib.SMTP_SSL('smtpout.secureserver.net', 465)
        # mailserver.ehlo()  # Say hello to the server
        # mailserver.login(sender_email, password)
        mailserver.sendmail(sender_email, receiver_email, msg.as_string())

        # Disconnect from the server
        # mailserver.quit()

        logging.info("Email sent successfully!")
    
        response = {
            "status_code": 200,
            "message": "OTP sent successfully"
            }

    except smtplib.SMTPServerDisconnected as e:
        logging.error(f"SMTPServerDisconnected: {e}")
    except smtplib.SMTPAuthenticationError as e:
        logging.error(f"SMTPAuthenticationError: {e}")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
    finally:
        output = insert_in_db(username, email, otp, request_id)
        logging.info(f"DB response {output}")
        return response
        