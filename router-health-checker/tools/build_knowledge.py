"""Builds the comprehensive 120+ Q&A knowledge base for Router Health Checker."""
import json
from pathlib import Path

def generate_kb():
    qa_list = [
        # --- 1. CORE SCAN RISKS & CONCEPTS ---
        {
            "id": "KB_001",
            "category": "scan_risks",
            "keywords": ["wps", "pin", "wps button", "8 digit"],
            "question": "What is WPS and why is it dangerous?",
            "answer": "WPS (Wi-Fi Protected Setup) lets devices connect using an 8-digit PIN or push button. The 8-digit PIN only has 11,000 effective combinations and can be brute-forced in a few hours using automated tools. Turning off WPS in your router settings keeps your network much safer! 🔓➡️🔒"
        },
        {
            "id": "KB_002",
            "category": "scan_risks",
            "keywords": ["telnet", "port 23", "remote management"],
            "question": "What is Telnet (port 23) and why is it a risk?",
            "answer": "Telnet is an ancient remote control tool that sends all data, including usernames and passwords, in unencrypted plain text. Anyone on the network can intercept your credentials. You should always disable Telnet and use SSH or HTTPS instead. 🚪❌"
        },
        {
            "id": "KB_003",
            "category": "scan_risks",
            "keywords": ["admin password", "default password", "admin admin", "factory password"],
            "question": "Why must I change the router admin password?",
            "answer": "Most routers come with default logins like 'admin/admin' or 'admin/password'. Attackers and malware know these factory defaults by heart. Changing it to a unique password of 12+ characters blocks unauthorized access to your router's settings. 🔑"
        },
        {
            "id": "KB_004",
            "category": "scan_risks",
            "keywords": ["wpa2", "wpa3", "wep", "encryption", "wifi security"],
            "question": "What is the difference between WEP, WPA2, and WPA3?",
            "answer": "WEP is obsolete and can be cracked in under 2 minutes. WPA2 is the current reliable standard for homes. WPA3 is the newest standard with modern encryption and protection against offline dictionary guesses. Always choose WPA2-AES or WPA3! 📶🛡️"
        },
        {
            "id": "KB_005",
            "category": "scan_risks",
            "keywords": ["open wifi", "no password", "public wifi"],
            "question": "Why is an open Wi-Fi network dangerous?",
            "answer": "An open Wi-Fi network has zero encryption. Anyone nearby can capture unencrypted traffic, see visited domains, and potentially redirect you to phishing websites. Always secure your Wi-Fi with a strong passphrase! ⚠️"
        },
        {
            "id": "KB_006",
            "category": "scan_risks",
            "keywords": ["upnp", "port 1900", "universal plug and play"],
            "question": "What is UPnP and why is it flagged?",
            "answer": "UPnP allows devices like game consoles and smart TVs to open router ports automatically. However, malware on infected laptops can abuse UPnP to punch holes in your router's firewall without your knowledge. Disabling UPnP adds extra security. ⚙️"
        },
        {
            "id": "KB_007",
            "category": "scan_risks",
            "keywords": ["tr069", "tr-069", "port 7547", "cwmp"],
            "question": "What is TR-069 (CWMP)?",
            "answer": "TR-069 is a protocol used by Internet Service Providers (ISPs) to configure and update your router remotely. If port 7547 is exposed to the local network or internet with known vulnerabilities, attackers can compromise the router. 📡"
        },
        {
            "id": "KB_008",
            "category": "scan_risks",
            "keywords": ["dns", "dns spoofing", "dns server", "resolver"],
            "question": "What is DNS and why does the scanner check it?",
            "answer": "DNS (Domain Name System) translates website names (like google.com) into IP addresses. If an attacker or rogue setting changes your router's DNS to a malicious server, you could be silently redirected to fake banking or phishing pages. 🌍"
        },
        {
            "id": "KB_009",
            "category": "scan_risks",
            "keywords": ["http admin", "plain http", "https"],
            "question": "Why should the router admin page use HTTPS?",
            "answer": "When you log into your router over plain HTTP (port 80), your admin password travels across the local Wi-Fi unencrypted. Enabling HTTPS encrypts your session so family members or guests cannot sniff the password. 🔒"
        },
        {
            "id": "KB_010",
            "category": "scan_risks",
            "keywords": ["firmware", "router update", "patch"],
            "question": "How often should I update router firmware?",
            "answer": "Check for firmware updates every 3 to 6 months in your router's management page. Firmware updates fix critical security flaws, patch vulnerabilities, and improve Wi-Fi speed and stability. 🧩"
        },
        {
            "id": "KB_011",
            "category": "scan_risks",
            "keywords": ["ssh", "port 22"],
            "question": "Is SSH (port 22) safe on my router?",
            "answer": "SSH provides encrypted command-line access. While far safer than Telnet, it should only be enabled if you actively use it for administration, and should always require a strong non-default password or cryptographic key. 💻"
        },
        {
            "id": "KB_012",
            "category": "scan_risks",
            "keywords": ["ftp", "port 21"],
            "question": "What does open port 21 (FTP) mean on a router?",
            "answer": "Port 21 is File Transfer Protocol, often used when a USB storage drive is plugged into the router. Plain FTP transmits credentials unencrypted. If you don't use router USB sharing, disable the FTP service in settings. 📁"
        },
        {
            "id": "KB_013",
            "category": "scan_risks",
            "keywords": ["ssid", "hide ssid", "hidden network"],
            "question": "Does hiding my Wi-Fi SSID make it safe?",
            "answer": "Hiding the SSID (network name) provides only minor security through obscurity. Free Wi-Fi scanner tools can still detect the hidden beacon frames when devices connect. Strong WPA2/WPA3 encryption is the true defense. 🕵️"
        },
        {
            "id": "KB_014",
            "category": "scan_risks",
            "keywords": ["mac filtering", "mac address whitelist"],
            "question": "Is MAC address filtering effective?",
            "answer": "MAC filtering allows only listed hardware addresses to connect. While helpful for keeping casual users off, MAC addresses can be easily spoofed by tech-savvy users. Use it only as a supplementary measure alongside WPA2/WPA3. 🏷️"
        },
        {
            "id": "KB_015",
            "category": "scan_risks",
            "keywords": ["firewall", "router firewall", "spi"],
            "question": "What is SPI Firewall in router settings?",
            "answer": "Stateful Packet Inspection (SPI) tracks active connections and blocks unsolicited incoming traffic from the internet. Keep SPI Firewall enabled at all times to defend all devices on your local network. 🧱"
        },
        {
            "id": "KB_016",
            "category": "scan_risks",
            "keywords": ["remote management", "wan access"],
            "question": "What is 'Remote Management' or 'WAN Access'?",
            "answer": "Remote Management allows logging into your router from outside your home over the internet. Unless you are a network administrator needing remote access, always keep this feature DISABLED to avoid global internet probes. 🌐🛑"
        },

        # --- 2. POPULAR ROUTER BRANDS STEP-BY-STEP ---
        {
            "id": "KB_017",
            "category": "brands",
            "keywords": ["tp-link", "tplink", "archer", "deco"],
            "question": "How do I secure a TP-Link router?",
            "answer": "1. Connect to Wi-Fi and open http://tplinkwifi.net or 192.168.0.1.\n2. Log in with your admin credentials.\n3. Go to System Tools → Password to change the admin password.\n4. Go to Wireless → Wireless Security and choose WPA2-PSK (AES).\n5. Go to Wireless → WPS and click 'Disable WPS'.\n6. Save and reboot. 🛡️"
        },
        {
            "id": "KB_018",
            "category": "brands",
            "keywords": ["d-link", "dlink", "dir"],
            "question": "How do I secure a D-Link router?",
            "answer": "1. Open http://192.168.0.1 in your browser.\n2. Log in with 'admin' and your password.\n3. Go to Tools → Admin to set a strong administrator password.\n4. Go to Setup → Wireless Settings → Manual Configuration.\n5. Set Security Mode to WPA-Personal with AES cipher.\n6. Under Advanced Wireless, disable Wi-Fi Protected Setup (WPS). 🔧"
        },
        {
            "id": "KB_019",
            "category": "brands",
            "keywords": ["netgear", "nighthawk", "orbi"],
            "question": "How do I secure a Netgear router?",
            "answer": "1. Open http://routerlogin.net or 192.168.1.1.\n2. Enter default or custom admin credentials.\n3. Navigate to ADVANCED → Administration → Set Password.\n4. Under Wireless Settings, verify Security Options is set to WPA2-PSK [AES].\n5. Go to ADVANCED → Advanced Setup → Wireless Settings and uncheck 'Keep Existing WPS Settings' to disable WPS. 📶"
        },
        {
            "id": "KB_020",
            "category": "brands",
            "keywords": ["tenda", "nova"],
            "question": "How do I configure security on a Tenda router?",
            "answer": "1. Open http://192.168.0.1 or tendawifi.com.\n2. Navigate to Administration → Login Password and update it.\n3. Go to Wireless Settings → Security Mode and choose WPA2-PSK.\n4. In Administration, uncheck 'Remote Web Management'.\n5. Save and reboot your router. ⚡"
        },
        {
            "id": "KB_021",
            "category": "brands",
            "keywords": ["asus", "rt-ac", "rt-ax", "asuswrt"],
            "question": "How do I secure an Asus router?",
            "answer": "1. Open http://router.asus.com or 192.168.1.1.\n2. Go to Administration → System to change the router login name and password.\n3. Go to Wireless → General, select WPA2/WPA3-Personal with AES.\n4. Go to Wireless → WPS tab and toggle 'Enable WPS' to OFF.\n5. Enable AiProtection under General settings for automatic threat blocking! 🛡️"
        },
        {
            "id": "KB_022",
            "category": "brands",
            "keywords": ["jio", "jiofiber", "jio fiber"],
            "question": "How do I secure a JioFiber home gateway?",
            "answer": "1. Connect to your Jio Wi-Fi and open http://192.168.29.1.\n2. Log in with your admin credentials (default is often admin/Jiocentrum).\n3. Change your login password immediately under Administration.\n4. Go to Network → Wireless (2.4G / 5G) and ensure WPA2/WPA3 is enabled.\n5. You can also manage security settings and connected devices conveniently through the MyJio smartphone app! 📱"
        },
        {
            "id": "KB_023",
            "category": "brands",
            "keywords": ["airtel", "airtel xstream", "xstream fiber"],
            "question": "How do I secure an Airtel Xstream Fiber router?",
            "answer": "1. Open http://192.168.1.1 in your browser.\n2. Log in with admin credentials.\n3. Under Maintenance / User Account, change the default web password.\n4. Under WLAN settings, confirm encryption is WPA2-PSK with AES cipher.\n5. Disable WPS in the Advanced Wireless section. 🚀"
        },
        {
            "id": "KB_024",
            "category": "brands",
            "keywords": ["bsnl", "syrotech", "netlink", "ftth"],
            "question": "How do I secure a BSNL FTTH (Syrotech/Netlink) ONT router?",
            "answer": "1. Open http://192.168.1.1.\n2. Log in (common factory logins are admin/admin or admin/stdonut).\n3. Go to Management → User Management and replace the default password.\n4. Go to Network → WLAN → Security, select WPA2-PSK with AES.\n5. Go to Application → Daily Maintenance to disable Telnet and UPnP. 🌐"
        },
        {
            "id": "KB_025",
            "category": "brands",
            "keywords": ["act", "act fibernet"],
            "question": "How do I secure an ACT Fibernet Wi-Fi router?",
            "answer": "1. Connect to ACT Wi-Fi and browse to http://192.168.1.1 or 192.168.0.1.\n2. Log in with your admin credentials.\n3. Navigate to System Settings → Password to choose a strong password.\n4. In Wireless Security, pick WPA2-Personal.\n5. Turn off WPS and save settings. 🛡️"
        },
        {
            "id": "KB_026",
            "category": "brands",
            "keywords": ["huawei", "ont", "echolife"],
            "question": "How do I configure security on a Huawei router?",
            "answer": "1. Open http://192.168.100.1 or 192.168.8.1.\n2. Log in with your administrator account.\n3. Go to System Tools → Modify Login Password.\n4. Go to WLAN → 2.4G/5G Basic Network Settings and choose WPA2 PreSharedKey.\n5. Turn off WPS and disable Telnet under Security Configuration. 🔑"
        },
        {
            "id": "KB_027",
            "category": "brands",
            "keywords": ["linksys", "velop"],
            "question": "How do I secure a Linksys router?",
            "answer": "1. Open http://192.168.1.1 or linksyssmartwifi.com.\n2. Sign in to your local router administrator account.\n3. Go to Connectivity → Administration to change the Router Password.\n4. Go to Wi-Fi Settings → Basic and set Security Mode to WPA2 Personal.\n5. Under Wi-Fi Protected Setup, toggle the feature OFF. ⚡"
        },
        {
            "id": "KB_028",
            "category": "brands",
            "keywords": ["xiaomi", "mi router"],
            "question": "How do I secure a Xiaomi Mi Router?",
            "answer": "1. Open http://192.168.31.1 or miwifi.com.\n2. Enter your management password.\n3. In Settings → Wi-Fi Settings, configure WPA2/WPA3 mixed encryption.\n4. In Settings → Security, enable anti-rub network protection to block unknown devices.\n5. Update to the latest firmware under System Status. 📱"
        },

        # --- 3. SCORING, DASHBOARD & USAGE ---
        {
            "id": "KB_029",
            "category": "app_usage",
            "keywords": ["score", "scoring", "how score calculated", "points"],
            "question": "How is my router health score calculated?",
            "answer": "Your score starts at a perfect 100 points. Points are deducted for vulnerabilities:\n• Default admin password: -25 pts\n• Open Wi-Fi (no password): -25 pts\n• Telnet port 23 open: -20 pts\n• WEP encryption: -20 pts\n• WPS enabled: -10 pts\n• Plain HTTP admin: -10 pts\n• Suspicious DNS: -10 pts\n• Exposed UPnP/TR-069: -5 pts each.\nFixing weak items restores your score! 💯"
        },
        {
            "id": "KB_030",
            "category": "app_usage",
            "keywords": ["score meaning", "excellent", "good", "fair", "risky"],
            "question": "What do the score ratings mean?",
            "answer": "• 90-100 (🟢 Excellent): Outstanding security; best practices followed.\n• 75-89 (🟡 Good): Safe for daily use with minor tweaks recommended.\n• 50-74 (🟠 Fair/Needs Attention): Moderate risks detected that should be addressed.\n• Below 50 (🔴 Risky): Critical weaknesses like default logins or open Telnet present. 🛡️"
        },
        {
            "id": "KB_031",
            "category": "app_usage",
            "keywords": ["top 3 fixes", "top fixes", "how to fix"],
            "question": "What are the 'Top 3 Fixes'?",
            "answer": "Instead of overwhelming you with technical logs, Router Health Checker analyzes all findings and sorts them by points gain. We present the 3 most impactful actions you can take in 5 minutes to boost your score the fastest! 🛠️"
        },
        {
            "id": "KB_032",
            "category": "app_usage",
            "keywords": ["how to use", "run scan", "start check"],
            "question": "How do I run a router health check?",
            "answer": "1. Ensure your laptop or phone is connected to your Wi-Fi.\n2. Click the 'Router Check' tab in the navigation.\n3. Click the big 'Start scan' button.\n4. Wait 15-20 seconds while the 6 diagnostic checks run.\n5. Review your score and follow the Top 3 Fix cards! ⏱️"
        },
        {
            "id": "KB_033",
            "category": "app_usage",
            "keywords": ["stability", "ping", "jitter", "packet loss"],
            "question": "What does the Network Stability page measure?",
            "answer": "Stability measures how steady and reliable your connection is over time:\n• Ping (latency): Time taken for signals to travel (lower is better, ideally < 30ms).\n• Jitter: Variation in latency (lower is better, ideally < 5ms).\n• Packet Loss: Lost transmissions (should be 0%). 📈"
        },
        {
            "id": "KB_034",
            "category": "app_usage",
            "keywords": ["speed test", "download", "upload", "mbps"],
            "question": "How does the Speed test work?",
            "answer": "The Speed test sends and receives data through your Wi-Fi connection to calculate real-world megabits per second (Mbps). It checks whether your Wi-Fi throughput is smooth for HD streaming, zoom calls, or online gaming. ⚡"
        },
        {
            "id": "KB_035",
            "category": "app_usage",
            "keywords": ["wifi vs internet speed", "difference"],
            "question": "What is the difference between Wi-Fi speed and Internet speed?",
            "answer": "Wi-Fi speed is the speed between your device and your router antenna. Internet speed is the bandwidth from your router through your ISP to the outside world. If Wi-Fi speed is fast but Internet speed is slow, the bottleneck is your ISP plan or cable. 🛣️"
        },
        {
            "id": "KB_036",
            "category": "app_usage",
            "keywords": ["devices list", "who is connected", "connected devices"],
            "question": "How does the app find connected devices?",
            "answer": "The app queries your local network's Address Resolution Protocol (ARP) table in a read-only manner. It translates physical MAC addresses into recognizable hardware brands (Apple, Samsung, LG, Intel) so you can spot unwanted visitors. 📱💻"
        },
        {
            "id": "KB_037",
            "category": "app_usage",
            "keywords": ["unknown device", "unrecognized", "intruder"],
            "question": "What should I do if I see an 'Unknown device'?",
            "answer": "First check if someone in your home has a new phone, smart light, or smart plug. If nobody recognizes it, change your Wi-Fi password immediately. Changing the Wi-Fi password disconnects all devices until they re-authenticate with the new key. 🚫"
        },

        # --- 4. ENVIRONMENT-SPECIFIC ADVICE ---
        {
            "id": "KB_038",
            "category": "environments",
            "keywords": ["home", "family", "kids", "parental controls"],
            "question": "How do I make home Wi-Fi safe for children?",
            "answer": "1. Enable Parental Controls in your router to filter adult and malicious websites.\n2. Schedule Wi-Fi bedtime cutoffs for kids' devices.\n3. Use family-safe DNS like Cloudflare 1.1.1.3 (blocks malware + adult content).\n4. Keep the router in an open living area rather than locked away. 🏡"
        },
        {
            "id": "KB_039",
            "category": "environments",
            "keywords": ["hostel", "pg", "students", "shared wifi"],
            "question": "How do I protect myself on a shared hostel Wi-Fi?",
            "answer": "1. Turn on the firewall on your laptop (Windows Defender / macOS Firewall).\n2. Set your network profile to 'Public' so your laptop does not share folders or printers.\n3. Avoid accessing sensitive accounts without HTTPS or a trusted VPN.\n4. Encourage the hostel warden to run Router Health Checker to fix default passwords! 🎓"
        },
        {
            "id": "KB_040",
            "category": "environments",
            "keywords": ["shop", "small shop", "upi", "card machine", "billing"],
            "question": "How do I protect UPI and card billing devices in a small shop?",
            "answer": "1. Create two separate Wi-Fi networks: one private network for your billing PC, POS machine, and CCTV, and a separate 'Guest Wi-Fi' for customers.\n2. Never give customers the password to the billing network.\n3. Enable AP Isolation so customer phones cannot communicate with each other or your billing system. 🏪💳"
        },
        {
            "id": "KB_041",
            "category": "environments",
            "keywords": ["cctv", "smart camera", "iot"],
            "question": "How do I secure smart home devices and CCTV cameras?",
            "answer": "1. Change default passwords on every IP camera and smart bulb.\n2. Put IoT gadgets on a separate Guest 2.4 GHz network.\n3. Disable UPnP on your router so cameras cannot open ports to the global internet.\n4. Keep device firmware updated. 📹"
        },
        {
            "id": "KB_042",
            "category": "environments",
            "keywords": ["smart tv", "streaming box"],
            "question": "Can my Smart TV get hacked through Wi-Fi?",
            "answer": "Smart TVs run complete operating systems and are susceptible to network snooping if connected to unencrypted Wi-Fi. Ensure your TV is on a WPA2/WPA3 network, disable remote debug features, and turn off automatic microphone listening when not in use. 📺"
        },

        # --- 5. WI-FI PERFORMANCE & HYGIENE ---
        {
            "id": "KB_043",
            "category": "hygiene",
            "keywords": ["2.4 ghz", "5 ghz", "frequency", "dual band"],
            "question": "What is the difference between 2.4 GHz and 5 GHz Wi-Fi?",
            "answer": "• 2.4 GHz travels farther and passes through walls easily, but is slower and more crowded.\n• 5 GHz is much faster with lower latency and less interference, but has a shorter range.\nUse 5 GHz for laptops, gaming, and 4K TVs, and 2.4 GHz for smart home devices and distant rooms. 📶"
        },
        {
            "id": "KB_044",
            "category": "hygiene",
            "keywords": ["wifi channel", "channel selection", "interference"],
            "question": "How do I choose the best Wi-Fi channel?",
            "answer": "In the crowded 2.4 GHz band, only channels 1, 6, and 11 do not overlap. If your neighbor uses channel 6, set yours to 1 or 11. Most modern routers have an 'Auto' setting that selects the least congested channel on boot. 📻"
        },
        {
            "id": "KB_045",
            "category": "hygiene",
            "keywords": ["router location", "placement", "where to keep"],
            "question": "Where is the best place to put a Wi-Fi router?",
            "answer": "Place your router in a central, elevated location (like on a shelf or desk). Keep it away from metal objects, thick concrete walls, mirrors, and microwaves, which absorb or reflect radio signals. 📍"
        },
        {
            "id": "KB_046",
            "category": "hygiene",
            "keywords": ["guest network", "guest wifi"],
            "question": "What is a Guest Network and should I use it?",
            "answer": "A Guest Network creates a secondary Wi-Fi name for visitors. It grants internet access while isolating guests from your private files, smart TVs, and network storage. It is one of the most effective security habits for homes and offices! 👥"
        },
        {
            "id": "KB_047",
            "category": "hygiene",
            "keywords": ["strong password", "passphrase", "how to create password"],
            "question": "How do I create a strong Wi-Fi password?",
            "answer": "Use a memorable 4-word passphrase rather than a short complex code. For example: 'Blue$Mountain$River$Walk!'. It is over 20 characters long, virtually impossible to brute-force, yet easy for family members to type. Avoid phone numbers, birthdays, and pet names. 🔑"
        },
        {
            "id": "KB_048",
            "category": "hygiene",
            "keywords": ["reboot", "restart router", "turn off and on"],
            "question": "Does restarting my router improve speed?",
            "answer": "Yes! Routers are mini-computers with RAM and a CPU. Periodic restarts clear temporary cache buffers, discard stale connections, and trigger automatic channel selection to avoid neighbor interference. 🔄"
        },
        {
            "id": "KB_049",
            "category": "hygiene",
            "keywords": ["dns recommendation", "best dns", "cloudflare", "google dns"],
            "question": "Which public DNS servers are recommended?",
            "answer": "• Cloudflare: 1.1.1.1 and 1.0.0.1 (Fastest, zero logging privacy).\n• Google: 8.8.8.8 and 8.8.4.4 (Reliable global availability).\n• Quad9: 9.9.9.9 (Blocks known malicious domains automatically).\nConfiguring these on your router protects every device automatically! 🌍"
        },
        {
            "id": "KB_050",
            "category": "hygiene",
            "keywords": ["vpn", "router vpn", "virtual private network"],
            "question": "Can I install a VPN directly on my router?",
            "answer": "Yes, many modern routers (Asus, Netgear, DD-WRT, OpenWrt) support OpenVPN or WireGuard clients. Setting up a VPN on the router automatically encrypts internet traffic for all connected smart TVs and phones without installing apps on each one. 🛡️"
        },

        # --- 6. TROUBLESHOOTING & APP HELP ---
        {
            "id": "KB_051",
            "category": "troubleshooting",
            "keywords": ["cannot find gateway", "gateway ip not found", "error gateway"],
            "question": "What should I do if the app cannot find my gateway IP?",
            "answer": "1. Confirm your computer or phone is connected to your router via Wi-Fi or Ethernet cable.\n2. Most routers use 192.168.1.1 or 192.168.0.1.\n3. You can manually enter your gateway IP in the scan bar and click 'Start scan'. 🔍"
        },
        {
            "id": "KB_052",
            "category": "troubleshooting",
            "keywords": ["scan blocked", "firewall blocked scan", "timeout"],
            "question": "Why did my scan time out or get blocked?",
            "answer": "Some high-security routers have aggressive ICMP flood prevention or local port blocking. Check that your laptop firewall allows local network discovery and that your rate limit hasn't exceeded 1 scan per 30 seconds. ⏳"
        },
        {
            "id": "KB_053",
            "category": "troubleshooting",
            "keywords": ["mic not working", "voice input error", "speech recognition"],
            "question": "Why is the microphone button not hearing me?",
            "answer": "1. Click the lock icon in your browser address bar and make sure 'Microphone' is set to Allow.\n2. Ensure your operating system microphone is not muted.\n3. Chrome and Edge offer the best support for Web Speech recognition. 🎤"
        },
        {
            "id": "KB_054",
            "category": "troubleshooting",
            "keywords": ["speed low", "slow speed", "buffering"],
            "question": "Why is my speed test result lower than my plan?",
            "answer": "1. If you are on 2.4 GHz Wi-Fi, maximum real-world throughput is usually 30-50 Mbps. Switch to the 5 GHz band for full speed.\n2. Move closer to the router to avoid wall attenuation.\n3. Disconnect heavy downloads on other devices during the test. ⚡"
        },
        {
            "id": "KB_055",
            "category": "troubleshooting",
            "keywords": ["reset router", "factory reset", "pin hole"],
            "question": "How do I factory reset my router if I forgot the password?",
            "answer": "With the router powered on, press and hold the tiny 'Reset' pinhole button on the back for 10-15 seconds using a paperclip until all lights flash. Note: This restores factory defaults, so you will need to re-enter your ISP credentials and set a new Wi-Fi password. 📌"
        },

        # --- 7. ETHICS, LAW & SAFE REFUSALS ---
        {
            "id": "KB_056",
            "category": "ethics_and_law",
            "keywords": ["it act", "section 43", "section 66", "cyber law"],
            "question": "What does the Indian IT Act 2000 say about network testing?",
            "answer": "Under Sections 43 and 66 of the Information Technology Act 2000, accessing, scanning, or altering computer systems or networks without explicit permission is an illegal offense carrying civil compensation and criminal imprisonment. Always test only your own network! ⚖️"
        },
        {
            "id": "KB_057",
            "category": "ethics_and_law",
            "keywords": ["own network", "permission", "defensive"],
            "question": "Why does Router Health Checker only allow private IP scans?",
            "answer": "To enforce safe and ethical principles. Scanning private subnets (192.168.x.x, 10.x.x.x) ensures the tool evaluates only your own local network environment, preventing misuse against internet servers or external domains. 🌿"
        },
        {
            "id": "KB_058",
            "category": "ethics_and_law",
            "keywords": ["crack wifi", "hack neighbor", "break password", "hack wifi"],
            "question": "How do I crack my neighbor's Wi-Fi password?",
            "answer": "🛡️ I cannot assist with cracking passwords or unauthorized access. Hacking into a neighbor's network is illegal and violates ethical computing standards. If you need Wi-Fi access, ask your neighbor or set up your own authorized connection. Let's focus on securing your own home! 🌿"
        },
        {
            "id": "KB_059",
            "category": "ethics_and_law",
            "keywords": ["bypass password", "bypass login", "exploit router"],
            "question": "Can this app help me bypass someone else's router login?",
            "answer": "🛡️ No. Router Health Checker is strictly a defensive, read-only audit tool. It never performs exploits, brute-force cracking, or unauthorized bypasses. Its sole purpose is to help you protect your own network. 🔒"
        },
        {
            "id": "KB_060",
            "category": "ethics_and_law",
            "keywords": ["privacy", "data collection", "does data leave"],
            "question": "Does my router data or password leave my laptop?",
            "answer": "No. Router Health Checker is built with Privacy by Design. All scan diagnostics, ARP tables, and test history remain stored in your local SQLite database on your device. Nothing is uploaded to any cloud server! 🔐"
        }
    ]

    # Generate additional 65 entries to reach 125 total across all categories
    topics = [
        ("WPA3 Enterprise vs Personal", "WPA3 Personal uses SAE (Simultaneous Authentication of Equals) for homes, while Enterprise uses 802.1X RADIUS authentication for corporate workstations. 🏢", ["wpa3 enterprise", "radius"]),
        ("Wi-Fi 6 and Wi-Fi 6E Benefits", "Wi-Fi 6 (802.11ax) introduces OFDMA and Target Wake Time for better device density and battery savings; 6E adds the clean 6 GHz spectrum. 🚀", ["wifi 6", "wifi 6e", "802.11ax"]),
        ("What is Mesh Wi-Fi?", "Mesh Wi-Fi uses multiple linked nodes under a single network name to blanket large homes in seamless signal without manual switching. 🕸️", ["mesh wifi", "mesh", "nodes"]),
        ("What is AP Isolation?", "AP (Access Point) Isolation blocks wireless devices on the same Wi-Fi from talking to each other, preventing lateral malware spread. 🛡️", ["ap isolation", "client isolation"]),
        ("Why avoid default SSIDs?", "Default names like 'NETGEAR_5G' or 'TP-LINK_B2' reveal the router make and model, helping attackers identify firmware vulnerabilities. Give your Wi-Fi a custom name! 🏷️", ["default ssid", "change ssid"]),
        ("Can Wi-Fi cause radiation harm?", "Non-ionizing RF signals from Wi-Fi routers operate well within international safety limits (FCC/ICNIRP) and do not damage cellular DNA. 📡", ["radiation", "safety health"]),
        ("What is Band Steering?", "Band Steering automatically guides dual-band devices to the faster 5 GHz frequency when within range, freeing 2.4 GHz for distant devices. 🔄", ["band steering"]),
        ("What is Beamforming?", "Beamforming focuses Wi-Fi radio waves directly toward connected devices rather than broadcasting equally in all directions, improving range and throughput. 🎯", ["beamforming"]),
        ("What is MU-MIMO?", "Multi-User Multiple Input Multiple Output allows a router to communicate with multiple devices simultaneously rather than queuing them in sequence. 🏎️", ["mu-mimo", "mimo"]),
        ("What is Port Forwarding?", "Port forwarding directs inbound internet traffic on a specific port to a local device (like a Minecraft server or NAS). Close unused port forward rules! 🚪", ["port forwarding", "forward ports"]),
        ("What is a DMZ host in router settings?", "A Demilitarized Zone (DMZ) exposes a single local device completely outside the router's firewall. Never place a personal PC or billing machine in DMZ! ⚠️", ["dmz", "dmz host"]),
        ("What is DDNS (Dynamic DNS)?", "Dynamic DNS maps a changing residential IP address to a fixed domain name (like myhome.ddns.net) for remote access. 🌐", ["ddns", "dynamic dns"]),
        ("What is QoS (Quality of Service)?", "QoS prioritizes important network traffic (like Zoom calls or online gaming) over background file downloads to prevent lag. 📊", ["qos", "quality of service"]),
        ("How to secure router USB file sharing?", "Disable anonymous guest read/write access and mandate strong authenticated user accounts for any hard drive plugged into the router USB port. 💾", ["usb sharing", "samba", "dlna"]),
        ("What is a captive portal?", "A captive portal forces web browsers to view a login or terms page before granting internet access, popular in hotels and cafes. 🏨", ["captive portal"]),
        ("What is Evil Twin Wi-Fi attack?", "An attacker sets up a fake rogue Wi-Fi hotspot with the exact same name as your home network to steal passwords. WPA3 prevents this via SAE! 👥⚠️", ["evil twin", "rogue ap"]),
        ("What is Wi-Fi Deauthentication attack?", "Deauth attacks send spoofed frames to disconnect devices from Wi-Fi. WPA3 Protected Management Frames (PMF) completely block deauth attacks! 🚫", ["deauth", "pmf"]),
        ("What is KRACK vulnerability?", "Key Reinstallation Attacks targeted WPA2 handshakes. Modern router firmware updates patched KRACK, which is why updating firmware is crucial! 🧩", ["krack", "wpa2 vulnerability"]),
        ("What is DNS-over-HTTPS (DoH)?", "DoH encrypts DNS lookups inside standard HTTPS traffic, preventing your ISP or local eavesdroppers from viewing which websites you visit. 🔒", ["doh", "dns over https"]),
        ("What is DNS-over-TLS (DoT)?", "DoT encrypts DNS requests over dedicated port 853, guaranteeing domain privacy and data integrity against tampering. 🛡️", ["dot", "dns over tls"]),
        ("How to protect against Wi-Fi sniffing?", "Always ensure Wi-Fi encryption is WPA2/WPA3 and visit websites using HTTPS (padlock icon in browser) so network packets remain encrypted. 🕵️", ["sniffing", "packet capture"]),
        ("What is MAC address randomization?", "Modern Android and iPhones use randomized virtual MAC addresses when scanning networks to prevent retail trackers from logging movement. 📱", ["random mac", "mac randomization"]),
        ("How to secure Wi-Fi in student PG?", "Request the PG owner to enable AP isolation, never use shared file folders, and keep an active firewall on your laptop. 🎓", ["pg wifi", "paying guest"]),
        ("How to backup router configuration?", "Go to System Tools → Backup & Restore and save the config file to a secure offline drive before modifying advanced settings. 💾", ["backup config", "restore config"]),
        ("What is MTU size in router settings?", "Maximum Transmission Unit (standard 1500 bytes) sets the largest packet size. Incorrect MTU causes packet fragmentation and sluggish browsing. 📏", ["mtu", "packet size"]),
        ("Can malware infect a router?", "Yes, botnets like Mirai and Mozi scan for default admin passwords and unpatched firmware to turn routers into DDoS drones. 🤖", ["router malware", "mirai botnet"]),
        ("What is WPS PIN brute force (Reaver)?", "Tools like Reaver exploit the half-PIN design flaw in WPS to recover the Wi-Fi password. Disabling WPS completely neutralizes this attack! 🔓", ["reaver", "wps brute force"]),
        ("How does Router Health Checker protect privacy?", "All port probes and diagnostics execute on your local CPU; no scan data or telemetry is sent across the internet. 🌿", ["privacy policy", "data protection"]),
        ("How to clean router dust and prevent overheating?", "Power down the router and gently blow compressed air through the ventilation grilles. Overheating causes CPU throttling and sudden Wi-Fi drops. 💨", ["dust", "overheating"]),
        ("What is a Wi-Fi Extender vs Mesh?", "Extenders repeat signals on a degraded half-duplex channel; Mesh systems use dedicated backhaul channels for full speed throughout the house. 📶", ["extender", "repeater"]),
        ("What is Wi-Fi protected management frames (PMF)?", "PMF protects management frames from forgery, preventing malicious disconnection attacks. It is mandatory on WPA3. 🛡️", ["pmf", "802.11w"]),
        ("How to protect billing machine in restaurant?", "Set up a VLAN or isolated SSID dedicated strictly to point-of-sale machines, separating it from customer public Wi-Fi. 🍽️", ["restaurant wifi", "pos machine"]),
        ("What is a double NAT issue?", "Connecting a router behind another ISP modem-router creates two layers of network translation, causing gaming and port forwarding errors. Use Bridge Mode! 🌉", ["double nat", "bridge mode"]),
        ("What is Bridge Mode?", "Bridge Mode turns an ISP gateway into a pure modem, letting your private high-performance router manage firewall and IP assignments. 🌉", ["bridge mode", "ont bridge"]),
        ("What is DHCP lease time?", "Lease time specifies how long a device retains its assigned local IP address before renewing. 24 hours is standard for home networks. ⏱️", ["dhcp", "lease time"]),
        ("What is Static IP reservation?", "Static reservation binds a specific private IP (e.g. 192.168.1.50) to a printer or NAS MAC address so it never changes address. 📌", ["static ip", "ip reservation"]),
        ("What is ICMP ping flooding?", "Sending massive ping requests can overwhelm old routers. The router's 'Ignore Ping from WAN' option defends against external probes. 🌊", ["ping flood", "icmp"]),
        ("Why does my router have 2 default passwords?", "Many routers have one password for Wi-Fi access and a separate, higher-privilege password for the administration settings page. Change BOTH! 🔑🔑", ["two passwords", "admin vs wifi"]),
        ("How to spot a phishing router login page?", "Always check the URL in the address bar. Real local router pages start with your gateway IP (e.g. 192.168.1.1), not an external domain. 🎣", ["phishing", "fake login"]),
        ("What is WPS Push Button (PBC)?", "Push Button Configuration allows pairing by pressing physical buttons on the router and printer within 2 minutes. It is safer than PIN mode but still best disabled. 🔘", ["pbc", "wps button"]),
        ("What is RTS/CTS threshold?", "Request to Send / Clear to Send threshold resolves the 'hidden node' problem where distant devices collide on the same channel. 📻", ["rts/cts"]),
        ("How to detect rogue Wi-Fi devices?", "Check the Connected Devices page in Router Health Checker weekly. Any device without an assigned family nickname should be investigated. 🕵️", ["rogue device"]),
        ("What is a Wi-Fi Jammer?", "Illegal devices that flood radio frequencies with noise to knock cameras and phones offline. Wired Ethernet links offer immunity against radio jamming. 🚫", ["jammer", "jamming"]),
        ("What is 802.11k / 802.11v / 802.11r?", "Fast roaming protocols that help phones seamlessly switch between mesh router nodes without dropping voice or video calls. 🏃", ["fast roaming", "802.11r"]),
        ("Why turn off WPS PIN in shop Wi-Fi?", "A customer sitting in your shop for 30 minutes can silently guess an 8-digit WPS PIN and compromise the entire network. Always disable WPS! 🔓🛑", ["shop wps"]),
        ("What is Router Health Streak?", "A family gamification feature that awards Safety Badges (Bronze, Silver, Gold Shield) as you maintain a score above 90 over successive weeks! 🏆", ["streak", "gamification", "badge"]),
        ("What is Elder Mode?", "A high-accessibility mode with extra large 20px typography, high contrast, and automatic voice read-aloud of findings. 🧓", ["elder mode", "senior"]),
        ("What is Kid Mode?", "A simplified storybook view explaining Wi-Fi security with house-and-key analogies and playful illustrations for young learners. 🧒", ["kid mode", "children"]),
        ("What is a Wi-Fi Heatmap?", "A visual map of your home showing signal strength gradients from green (strong) to red (dead zone) to guide router placement. 🗺️", ["heatmap", "signal coverage"]),
        ("How does offline AI mode work?", "Router Health Checker embeds an offline 120+ entry knowledge base so you receive immediate, accurate step-by-step guidance even if your internet is completely disconnected! 📴💡", ["offline ai", "offline mode"]),
        ("What is WPA3 Transition Mode?", "A mixed mode that allows modern WPA3 devices to connect with SAE while letting older gadgets use WPA2 on the same network name. 🔄", ["transition mode", "wpa2 wpa3 mixed"]),
        ("How to secure smart bulbs and plugs?", "Always connect inexpensive smart plugs to an isolated 2.4 GHz Guest Wi-Fi so a compromised bulb cannot access your laptop. 💡", ["smart bulb", "smart plug"]),
        ("What is BSS Coloring in Wi-Fi 6?", "BSS Coloring tags packets with digital color codes so routers ignore neighbor chatter on the same frequency, drastically reducing congestion. 🎨", ["bss coloring"]),
        ("How to read the router check audit log?", "Go to the Settings page to review the tamper-evident audit log showing timestamps, target IPs, and test results stored safely in SQLite. 📜", ["audit log"]),
        ("What is UPnP-IGD protocol?", "Internet Gateway Device protocol allows automated port mapping. Disabling UPnP prevents malicious applications from opening ports silently. 🔌", ["upnp igd"]),
        ("What is DNS rebinding attack?", "Malicious websites trick browsers into sending commands to local routers (192.168.1.1). Modern routers with DNS rebinding protection block these scripts. 🕸️", ["dns rebinding"]),
        ("Why does Router Health Checker warn on Telnet?", "Telnet transmits passwords without any cryptographic protection. Anyone listening on Wi-Fi can capture your credentials instantly. 🚪⚠️", ["telnet warning"]),
        ("How to export router health report?", "Click 'Download printable report' or 'Share with my family' on the Router Check page to save a clean, translated PDF summary of your score and fixes! 📄", ["export report", "print report", "pdf"]),
        ("What is the Family Safety Pledge?", "A commitment by household members to maintain strong passwords, keep devices updated, and never share primary Wi-Fi credentials with strangers. 🤝", ["safety pledge"]),
        ("What is Zero Trust in home networks?", "Treating every device—including smart TVs and guest phones—as potentially untrusted until verified, keeping critical devices isolated. 🛡️", ["zero trust"]),
        ("What is WPA2-Enterprise?", "Uses an authentication server (RADIUS) where every family member or employee has their own individual username and password instead of a shared passphrase. 🏢", ["wpa2 enterprise"]),
        ("How to inspect router logs?", "Log into your router admin page and navigate to System Log or Event Log to view recent connection attempts and firewall drops. 📑", ["router logs", "system log"]),
        ("What is WPS PIN lockout?", "A safety setting on modern routers that temporarily disables WPS after 3-5 failed PIN attempts to slow down brute-force attacks. 🔒", ["wps lockout"]),
        ("What is firmware rollback protection?", "Prevents attackers from downgrading your router to an older, vulnerable firmware release. Keep this option enabled! 🛡️", ["rollback protection"]),
        ("How to know if router is hacked?", "Signs include unfamiliar DNS settings, random pop-up ads on normal websites, changed admin passwords, and sluggish internet during idle hours. Run Router Health Checker to verify! 🚨", ["hacked router", "signs of hack"])
    ]

    for i, (q, a, kw) in enumerate(topics, start=61):
        qa_list.append({
            "id": f"KB_{i:03d}",
            "category": "extended_topics",
            "keywords": kw,
            "question": q,
            "answer": a
        })

    out_path = Path("C:/Users/nivin/.gemini/antigravity/scratch/router-health-checker/knowledge/qa.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"total": len(qa_list), "entries": qa_list}, f, indent=2, ensure_ascii=False)
    print(f"Successfully generated {len(qa_list)} Q&A entries in {out_path}")

if __name__ == "__main__":
    generate_kb()
