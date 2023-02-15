from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.action_chains import ActionChains
import threading
import time
import pickle

import pandas as pd
executable_path = "C:\webdriver\chromedriver.exe"

class Scraper:
    
    def __call__(self):
        
        # Changing chromedriver default options
        options = Options()
        options.headless = False # Change to False if you want it to happen visually
        options.add_argument("--start-maximized") #Headless = True
        
        max_workers = 1
        drivers = []
        threads = []
        dataframes = [pd.DataFrame() for _ in range(max_workers)]
        links = []

        def cookies(driver):
            driver.get('https://www.betcity.nl/sportsbook#sports-hub/football')
            
            # Cookie button
            try:
                WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, '//*[@id="CybotCookiebotDialogBodyButtonAccept"]')))
                time.sleep(5)
                driver.find_element(By.XPATH, '//*[@id="CybotCookiebotDialogBodyButtonAccept"]').click()
            except: 
                return
            
        # Scrapes a soccer league on Betcity
        def scrape(driver, link, worker):
            
            # List of team-names: ['teamname1'\n'teamname2', ....]
            names = []
            # List of hyperlinks to bets
            bet_links = []
            # List of 1x2 odds
            result_list = []
            # List of over/under odds
            over_under_list = []
            # List of first half over/under odds
            over_under_1e_list = []
            # List of second half over/under odds
            over_under_2e_list = []
            # List of handicap odds
            handicap_list = []
            # List of dubbele kans odds
            dubbele_kans_list = []
            # List of Beide teams scoren
            beide_teams_scoren_list = []
            # List of first half Beide teams scoren
            beide_teams_scoren_1e_list = []
            # List of second half Beide teams scoren
            beide_teams_scoren_2e_list = []
            
            def click(webElement):
                ActionChains(driver).move_to_element(webElement)
                webElement.click()
                
            def wait(xpath):
                try:
                    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, xpath)))
                except: 
                    return
                
            def scrape_result():
                # Find all 1x2 odds
                try:
                    result = driver.find_element(By.XPATH, ".//li[@class='KambiBC-bet-offer-subcategory KambiBC-bet-offer-subcategory--onecrosstwo']")
                except:
                    return False
                    
                # Add the teamnames to the right list
                teamNames = result.find_elements(By.XPATH, ".//div[@class='KambiBC-outcomes-list__column']/button/div/div[1]")
                names.append(teamNames[0].text + "\n" + teamNames[2].text)
                    
                # Add the result odds to the right list
                result_odds = result.find_elements(By.XPATH, ".//div[@class='KambiBC-outcomes-list__column']/button/div/div[2]")
                
                if len(result_odds) < 3:
                    result_list.append("1.0\n1.0\n1.0")
                    return True
                
                result_list.append(result_odds[0].text + "\n" + result_odds[1].text + "\n" + result_odds[2].text)
                return True
            
            def scrape_dubbele_kans():
                # Find all dubbele kans odds
                try:
                    dubbele_kans = driver.find_element(By.XPATH, ".//li[@class='KambiBC-bet-offer-subcategory KambiBC-bet-offer-subcategory--doublechance']")
                except:
                    dubbele_kans_list.append("1.0\n1.0\n1.0")
                    return
                    
                # Add all the dubbele kans odds to the right list
                dubbele_kans_odds = dubbele_kans.find_elements(By.XPATH, ".//div[@class='KambiBC-outcomes-list__column']/button/div/div[2]")
                
                if len(dubbele_kans_odds) < 3:
                    dubbele_kans_list.append(0)
                    return
                
                dubbele_kans_list.append(dubbele_kans_odds[0].text + "\n" + dubbele_kans_odds[1].text + "\n" + dubbele_kans_odds[2].text)
            
            def scrape_over_under():
                # The string that contains the odds for all over/under bets
                over_under_string = ""
                    
                # Find all over/under odds
                try:
                    over_under = driver.find_element(By.XPATH, ".//li[@class='KambiBC-bet-offer-subcategory KambiBC-bet-offer-subcategory--overunder']")
                except:
                    over_under_list.append(0)
                    return
                    
                # Show the over/under odds
                lijst_tonen(over_under)
                
                # Find the odds
                over_under_odds = over_under.find_elements(By.XPATH, ".//div[@class='KambiBC-outcomes-list__column']/button")
                  
                # The amount of over under odds
                n = int(len(over_under_odds)/2)
                
                # Add all the over under odds to a formatted string
                for i in range(n):
                    number = over_under_odds[i].find_element(By.XPATH, ".//div/div[1]/div[2]").text
                    try:
                        odd_over = over_under_odds[i].find_element(By.XPATH, ".//div/div[2]/div[2]").text
                    except:
                        odd_over = "1"
                    try:
                        odd_under = over_under_odds[i + n].find_element(By.XPATH, ".//div/div[2]/div[2]").text
                    except:
                        odd_under = "1"
                    over_under_string += number + "\n" + odd_over + "\n" + odd_under + "|"
                
                # Add all the over/under odds to the right list
                over_under_list.append(over_under_string)
            
            def scrape_beide_teams_scoren():
                # Find the beide teams scoren totaal odds
                try:
                    beide_teams_scoren = driver.find_element(By.XPATH, ".//li[div[div[div[h3[span[text()='Beide teams scoren']]]]]]")
                except:
                    beide_teams_scoren_list.append(0)
                    return
                    
                # Get all beide teams scoren odds on the game and then put them in the list
                beide_teams_scoren_odds = beide_teams_scoren.find_elements(By.XPATH, ".//div[@class='KambiBC-outcomes-list__column']/button/div/div[2]")
                
                if len(beide_teams_scoren_odds) < 2:
                    beide_teams_scoren_list.append(0)
                    return
                
                beide_teams_scoren_list.append(beide_teams_scoren_odds[0].text + "\n" + beide_teams_scoren_odds[1].text)
            
            def scrape_handicap():
                # The string that contains the odds for all handicaps
                handicap_string = ""
                    
                # Click to see all handicap bets
                try:
                    asian = driver.find_element(By.XPATH, ".//li[div[header[div[div[contains(text(), 'Asian Lines')]]]]]") 
                except:
                   handicap_list.append(0)
                   return
                    
                # Move to the asian subbets and open them
                click(asian)
                
                # Let the data load
                time.sleep(0.5)
                    
                # Find all handicap odds
                handicap = driver.find_element(By.XPATH, ".//li[@class='KambiBC-bet-offer-subcategory KambiBC-bet-offer-subcategory--asian']")
                    
                # Show the handicap odds
                lijst_tonen(handicap)
                    
                # Find the handicap odds
                numbers = handicap.find_elements(By.XPATH, ".//div[1][@class='KambiBC-outcomes-list__column']/button/div/div[1]/div[2]")
                handicap_home_odds = handicap.find_elements(By.XPATH, ".//div[1][@class='KambiBC-outcomes-list__column']/button/div/div[2]/div[2]")
                handicap_away_odds = handicap.find_elements(By.XPATH, ".//div[2][@class='KambiBC-outcomes-list__column']/button/div/div[2]/div[2]")
                    
                # Add all the handicap odds to a formatted string
                for i in range(len(handicap_home_odds)):
                    number = numbers[i].text
                    if number.find(".5") == -1:
                        continue
                    odd_home = handicap_home_odds[i].text
                    odd_away = handicap_away_odds[i].text
                    handicap_string += number + "\n" + odd_home + "\n" + odd_away + "|"
                
                # Add all the handicap odds to the right list
                handicap_list.append(handicap_string)
            
            def scrape_halves():
                # Click to see all half category bets
                try:
                    half = driver.find_element(By.XPATH, ".//li[div[header[div[div[contains(text(), 'Helft')]]]]]") 
                except:
                    over_under_1e_list.append(0)
                    over_under_2e_list.append(0)
                    beide_teams_scoren_1e_list.append(0)
                    beide_teams_scoren_2e_list.append(0)
                    return
                
                # Move to the half category subbets and open them
                click(half)
                
                # Let the data load
                time.sleep(0.5)
                
                # Scrape the over/under bets from the first half
                try:
                    scrape_over_under_1e(driver.find_element(By.XPATH, ".//li[div[div[div[h3[span[text()='Totaal aantal doelpunten - 1e Helft']]]]]]"))
                except:
                    over_under_1e_list.append(0)
                
                # Scrape the over/under bets from the second half
                try:
                    scrape_over_under_2e(driver.find_element(By.XPATH, ".//li[div[div[div[h3[span[text()='Totaal aantal doelpunten - 2e Helft']]]]]]"))
                except:
                    over_under_2e_list.append(0)
                
                # Scrape the beide teams winnen bets from the first half
                try:
                    scrape_beide_teams_scoren_1e(driver.find_element(By.XPATH, ".//li[div[div[div[h3[span[text()='Beide teams scoren - 1e Helft']]]]]]"))
                except:
                    beide_teams_scoren_1e_list.append(0)
                    
                # Scrape the over/under bets from the second half
                try:
                    scrape_beide_teams_scoren_2e(driver.find_element(By.XPATH, ".//li[div[div[div[h3[span[text()='Beide teams scoren - 2e Helft']]]]]]"))
                except:
                    beide_teams_scoren_2e_list.append(0)
                
            def scrape_over_under_1e(over_under):
                # The string that contains the odds for all over/under bets
                over_under_string = ""
                
                # Click on the lijst tonen button if it exists
                lijst_tonen(over_under)
                
                # Find the odds
                over_under_odds = over_under.find_elements(By.XPATH, ".//div[@class='KambiBC-outcomes-list__column']/button")
                
                # The amount of over under odds
                n = int(len(over_under_odds)/2)
                
                # Add all the over under odds to a formatted string
                for i in range(n):
                    number = over_under_odds[i].find_element(By.XPATH, ".//div/div[1]/div[2]").text
                    try:
                        odd_over = over_under_odds[i].find_element(By.XPATH, ".//div/div[2]/div[2]").text
                    except:
                        odd_over = "1"
                    try:
                        odd_under = over_under_odds[i + n].find_element(By.XPATH, ".//div/div[2]/div[2]").text
                    except:
                        odd_under = "1"
                    over_under_string += number + "\n" + odd_over + "\n" + odd_under + "|"
                
                # Add all the over/under odds to the right list
                over_under_1e_list.append(over_under_string)
                
            def scrape_over_under_2e(over_under):
                # The string that contains the odds for all over/under bets
                over_under_string = ""
                    
                # Click on the lijst tonen button if it exists
                lijst_tonen(over_under)
                
                # Find the odds
                over_under_odds = over_under.find_elements(By.XPATH, ".//div[@class='KambiBC-outcomes-list__column']/button")
                  
                # The amount of over under odds
                n = int(len(over_under_odds)/2)
                
                # Add all the over under odds to a formatted string
                for i in range(n):
                    number = over_under_odds[i].find_element(By.XPATH, ".//div/div[1]/div[2]").text
                    try:
                        odd_over = over_under_odds[i].find_element(By.XPATH, ".//div/div[2]/div[2]").text
                    except:
                        odd_over = "1"
                    try:
                        odd_under = over_under_odds[i + n].find_element(By.XPATH, ".//div/div[2]/div[2]").text
                    except:
                        odd_under = "1"
                    over_under_string += number + "\n" + odd_over + "\n" + odd_under + "|"
                
                # Add all the over/under odds to the right list
                over_under_2e_list.append(over_under_string)
                
            def scrape_beide_teams_scoren_1e(beide_teams_scoren):
                # Get all beide teams scoren odds on the game and then put them in the list
                beide_teams_scoren_odds = beide_teams_scoren.find_elements(By.XPATH, ".//div[@class='KambiBC-outcomes-list__column']/button/div/div[2]")
                
                if len(beide_teams_scoren_odds) < 2:
                    beide_teams_scoren_1e_list.append(0)
                    return
                
                beide_teams_scoren_1e_list.append(beide_teams_scoren_odds[0].text + "\n" + beide_teams_scoren_odds[1].text)
                
            def scrape_beide_teams_scoren_2e(beide_teams_scoren):
                # Get all beide teams scoren odds on the game and then put them in the list
                beide_teams_scoren_odds = beide_teams_scoren.find_elements(By.XPATH, ".//div[@class='KambiBC-outcomes-list__column']/button/div/div[2]")
                
                if len(beide_teams_scoren_odds) < 2:
                    beide_teams_scoren_2e_list.append(0)
                    return
                
                beide_teams_scoren_2e_list.append(beide_teams_scoren_odds[0].text + "\n" + beide_teams_scoren_odds[1].text)
            
            # A function that presses on Lijst tonen if it exists
            def lijst_tonen(webElement):
                try:
                    button = webElement.find_element(By.XPATH, ".//button[@class='KambiBC-outcomes-list__toggler-toggle-button']")
                except:
                    return
                
                click(button)
            
            driver.get(link)
            
            # The links of all singular matches
            matchLinks = []
        
            # Wait for the data to load
            try:
                wait(".//ul[@class='KambiBC-sandwich-filter__list']")
            except:
                print("Competition not found")
                return
        
            # Find all matches
            matches = driver.find_elements(By.XPATH, ".//li[@class='KambiBC-sandwich-filter__event-list-item']")
            
            # Loop through each match to extract the links
            for match in matches:
                current_day = time.localtime()[6]
                try:
                    match_day = match.find_element(By.XPATH, ".//span[@class='KambiBC-event-item__start-time--date']").text
                except:
                    continue
                
                if match_day == "ma":
                    match_day = 0
                elif match_day == "di":
                    match_day = 1
                elif match_day == "wo":
                    match_day = 2
                elif match_day == "do":
                    match_day = 3
                elif match_day == "vr":
                    match_day = 4
                elif match_day == "za":
                    match_day = 5
                elif match_day == "zo":
                    match_day = 6
                else:
                    continue
                
                date_diff = match_day - current_day
                if current_day != 6:
                    if date_diff < 0 or date_diff > 1 :
                        continue
                else:
                    if match_day != 0 and match_day != 6:
                        continue
                    
                link = match.find_element(By.XPATH, ".//a").get_attribute('href')
                try:
                    amount = int(match.find_element(By.XPATH, ".//div[@class='KambiBC-sandwich-filter_show-more-right-text']").text.split("B", 1)[0])
                except:
                    continue
                if link.find('live') == -1 and amount > 40:
                    matchLinks.append(link)
        
            # Visit each single match to extract the needed data
            for link in matchLinks:
                driver.get(link)
                
                # Wait for the data to load
                wait(".//button[@class='KambiBC-outcomes-list__toggler-toggle-button']")
                
                # Scrape the result data
                if not scrape_result():
                    continue
                
                bet_links.append(driver.current_url)
                
                # Scrape the dubbele kans data
                scrape_dubbele_kans()
                
                # Scrape the over/under data
                scrape_over_under()
                
                # Scrape the beide teams scoren data
                scrape_beide_teams_scoren()
                
                # Scrape the handicap data
                scrape_handicap()
                
                # Scrape the halves odds category data
                scrape_halves()
                
            # After each competition we create a dataframe with the odds that we have so far collected
            dict_worker = {'Teams': names, 'result' : result_list, 'over_under' : over_under_list, 'over_under_1e' : over_under_1e_list,
                        'over_under_2e' : over_under_2e_list, 'handicap' : handicap_list, 'beide_teams_scoren' : beide_teams_scoren_list,
                        'beide_teams_scoren_1e' : beide_teams_scoren_1e_list, 'beide_teams_scoren_2e' : beide_teams_scoren_2e_list, 'dubbele_kans' : dubbele_kans_list, 'bet_links' : bet_links}
        
            dataframes[worker] = pd.concat([dataframes[worker], pd.DataFrame.from_dict(dict_worker)])
        
        
        ## Run the Scraper
        start_time = time.time()
        
        with open('betcity_volly.txt', 'r') as f:
            links = f.read().split('\n')
        
        amount_links = len(links)
        links_used = 0
        
        for i in range(0, max_workers):
            drivers.append(webdriver.Chrome(executable_path=executable_path,options=options))
            
            threads.append(threading.Thread(target=cookies, args=[drivers[i]]))
            threads[i].start()
        
        while True:
            skip = False
            
            try:
                df_betcity = pd.concat([i for i in dataframes if not i.empty])
            except:
                skip = True
            
            stop = True
            
            for i in range(max_workers):
                if links_used >= amount_links:
                    if threads[i].is_alive():
                        stop = False
                        
                elif not threads[i].is_alive():
                    if links[links_used] == '':
                        links_used += 1
                        continue
                    
                    threads[i] = threading.Thread(target=scrape, args=[drivers[i], links[links_used], i])
                    threads[i].start()
                    links_used += 1
                    stop = False
                    
                else: stop = False
            
            if skip:
                continue
            
            output = open('df_betcity_volly', 'wb')
            pickle.dump(df_betcity, output)
            output.close()
            
            if stop:
                break
            
            time.sleep(1)
        
        for driver in drivers:
            driver.quit()
            
        print("Betcity finished in: %s seconds" % int((time.time() - start_time)))
        
Scraper.__call__(Scraper)