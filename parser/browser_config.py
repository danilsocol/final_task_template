from selenium.webdriver.chrome.options import Options

class BrowserConfig:
    @staticmethod
    def get_chrome_options():
        chrome_options = Options()
        
        # GPU settings
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-gpu-compositing')
        chrome_options.add_argument('--disable-gpu-rasterization')
        chrome_options.add_argument('--disable-gpu-sandbox')
        
        # Rendering settings
        chrome_options.add_argument('--disable-accelerated-2d-canvas')
        chrome_options.add_argument('--disable-accelerated-compositing')
        chrome_options.add_argument('--disable-accelerated-video-decode')
        chrome_options.add_argument('--disable-webgl')
        
        # WebRTC settings
        chrome_options.add_argument('--disable-webrtc')
        chrome_options.add_argument('--disable-webrtc-hw-encoding')
        chrome_options.add_argument('--disable-webrtc-hw-decoding')
        
        # Network settings
        chrome_options.add_argument('--disable-background-networking')
        chrome_options.add_argument('--disable-default-apps')
        chrome_options.add_argument('--no-default-browser-check')
        
        # Headless mode
        chrome_options.add_argument('--headless')
        
        return chrome_options 