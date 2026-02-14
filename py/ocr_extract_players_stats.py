import os
import re
import cv2
import requests
import easyocr
from concurrent.futures import ThreadPoolExecutor

# --- CONFIGURATION ---
# 1.53 KD is top 48%, 2.21 KD is top 19%, 2.64 KD is top 10%, 3.55 KD is top 3%,  4.60 KD is top 1% (source: https://www.bftracker.com/bf6/stats/pc/global)
GOD_SKILL_THRESHOLD = 6.0   # God-tier players with K/D above 6.0 (top ~0.3%)
ELITE_SKILL_THRESHOLD = 2.8  # Elite is above top 10%
HIGH_SKILL_THRESHOLD = 1.7  # High skill is the top 40% to 10%
LOW_SKILL_THRESHOLD = 1.4   # Low skill is below 50th percentile with a buffer (1.5 is 50th percentile) the gap between low and high skill is "average"
MAX_WORKERS = 10           # Parallel API requests
TARGET_FOLDER = "/ENTER/YOUR/PATH/"
MY_USERNAME = "PUT YOUR USERNAME"  # Set your own username to exclude from results
processed_players = set()  # Global set to track players across all images


# --- Comparative prevalence based on KD -> top% reference (see top-of-file comment) ---
def lerp(x, x0, y0, x1, y1):
    if x1 == x0: return y0
    t = (x - x0) / (x1 - x0)
    return y0 + t * (y1 - y0)

def est_top_percent(kd):
    # 1. Your data points (K/D, Top_Percent)
    # Note: I've added a 0.0 K/D anchor and ensured these are sorted by K/D
    pts = [
        (0.00, 100), (0.64, 95), (1.28, 63), (1.50, 50), (1.53, 48), 
        (2.03, 25), (2.21, 19), (2.64, 10), (3.55, 3), (4.60, 1), (6.25, 0.3),(28.20, 0.01)
    ]
    pts.sort() # Ensure K/D is ascending for the loop to work

    def lerp(x, x0, y0, x1, y1):
        # Standard linear interpolation formula
        return y0 + (x - x0) * (y1 - y0) / (x1 - x0)

    # Handle floor: if K/D is 0 or less
    if kd <= pts[0][0]:
        return 100.0
    
    # Handle ceiling: if K/D is higher than our max point
    if kd >= pts[-1][0]:
        return pts[-1][1]

    # Find the interval and interpolate
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        if x0 <= kd < x1:
            return lerp(kd, x0, y0, x1, y1)
    
    return pts[-1][1]

def fetch_single_player_stats(name):
    """
    1. Search for player identities (NucleusID and PersonaID).
    2. Batch query those specific IDs for real stats.
    This two-step approach improves the odds of finding players that the /bf6/stats/ endpoint might miss when searching by name alone.
    """
    search_url = f"https://api.gametools.network/bf6/player/"
    stats_url = "https://api.gametools.network/bf6/multiple/?categories=multiplayer&raw=false&format_values=true"
    secondary_stats_url = "https://api.gametools.network/bf6/stats/"  # Fallback for single player stats if needed
    
    try:
        # STEP 1: Try stats endpoint with name search first (some players might be found here directly)
        direct_stats_res = requests.get(secondary_stats_url, params={'name': name, 'categories': 'multiplayer', 'format_values': True, 'seperation': False}, timeout=30)

        if direct_stats_res.status_code == 200:
            data = direct_stats_res.json()
            total_kills = data.get("kills", 0)
            # If the API returns formatted strings like "1,200", remove the comma
            if isinstance(total_kills, str):
                total_kills = int(total_kills.replace(',', ''))
            
            if total_kills > 0:
                groups = data.get("gameModeGroups", [])
                stats = next((g for g in groups if g.get("gamemodeName") == "Multiplayer"), None)
                
                if stats:
                    if stats.get("killDeath") != 0:
                        return {
                            "name": name,
                            "platform": data.get("platform", "pc"),
                            "kd": float(stats.get("killDeath", 0)),
                            "win": float(stats.get("winPercent", "0").replace('%', ''))
                        }

        
        # STEP 2: Get the Player IDs
        search_res = requests.get(search_url, params={'name': name}, timeout=30)
        if search_res.status_code != 200:
            return None

        
        identities = search_res.json().get("results", [])
        if not identities or len(identities) == 0:
            return None

        # Prepare the payload for the POST request
        # We map nucleusId -> user_id and personaId -> player_id
        payload = []
        for identity in identities:
            payload.append({
                "player_id": int(identity.get("personaId")),
                "user_id": int(identity.get("nucleusId")),
                "platform": identity.get("platform", "pc")
            })


        # STEP 2: Fetch actual stats using the IDs
        stats_res = requests.post(stats_url, json=payload, timeout=30)
        if stats_res.status_code != 200:
            return None
        
        raw_data = stats_res.json()


        # --- DYNAMIC STRUCTURE HANDLING ---
        # 1. If it's a dict with a "data" key, extract that list
        if isinstance(raw_data, dict) and "data" in raw_data:
            results_list = raw_data["data"]
        # 2. If it's already a list, use it as is
        elif isinstance(raw_data, list):
            results_list = raw_data
        # 3. If it's a single dict (not in a list), wrap it in a list
        elif isinstance(raw_data, dict):
            results_list = [raw_data]
        else:
            return None

        
        # Iterate through the results to find the first profile with actual playtime/kills
        for data in results_list:
            total_kills = data.get("kills", 0)
            # If the API returns formatted strings like "1,200", remove the comma
            if isinstance(total_kills, str):
                total_kills = int(total_kills.replace(',', ''))
            
            if total_kills > 0:
                groups = data.get("gameModeGroups", [])
                stats = next((g for g in groups if g.get("gamemodeName") == "Multiplayer"), None)
                
                if stats:
                    if stats.get("killDeath") == 0:
                        continue  # Skip profiles with 0 K/D to find a more accurate one
                    return {
                        "name": name,
                        "platform": data.get("platform", "pc"),
                        "kd": float(stats.get("killDeath", 0)),
                        "win": float(stats.get("winPercent", "0").replace('%', ''))
                    }
                    
    except Exception as e:
        print(f"Error fetching {name}: {e}") # Debugging
        return None
        
    return None

def get_names_from_scoreboard(image_path):
    img = cv2.imread(image_path)
    if img is None: return []
    h, w, _ = img.shape

    # 1440p Crop Logic for leaderboard names
    blue_team = img[int(h*0.20):int(h*0.85), int(w*0.068):int(w*0.222)]
    red_team = img[int(h*0.20):int(h*0.85), int(w*0.545):int(w*0.72)]

    reader = easyocr.Reader(['en'])
    # Using width_ths=0.6 as you tweaked
    raw_results = reader.readtext(blue_team, width_ths=0.6) + reader.readtext(red_team, width_ths=0.6)
    with open("names.txt", "a") as f:
        for res in raw_results:
            f.write(res[1] + "\n")
    
    found_players = []
    for res in raw_results:
        text = res[1]
        # Remove level box [173]
        clean_text = re.sub(r'[^a-zA-Z0-9]?\d+[^a-zA-Z0-9]?$', '', text.strip())
        # Final cleanup
        clean_text = re.sub(r'[^a-zA-Z0-9_\-]', '', clean_text)
        if len(clean_text) > 2 and not clean_text.isdigit():
            found_players.append(clean_text)
            found_players.append(text.strip())  # Also keep the raw text since OCR can be inconsistent and we might find a better match in the raw text on subsequent screenshots
            
    return list(set(found_players))

def process_all_screenshots(folder_path):
    valid_extensions = ('.png', '.jpg', '.jpeg')
    files = sorted([f for f in os.listdir(folder_path) if f.lower().endswith(valid_extensions)])

    grand_total_kd, grand_total_win, total_players, total_god, total_elite, total_good, total_avg, total_bad = 0, 0, 0, 0, 0, 0, 0, 0

    for filename in files:
        full_path = os.path.join(folder_path, filename)
        print(f"\n--- Processing: {filename} ---")
        
        # Get all names found in the current screenshot
        all_names_in_image = get_names_from_scoreboard(full_path)
        
        # Filter out:
        # 1. Yourself
        # 2. Players we have already fetched in a previous screenshot
        unique_new_names = []
        for name in all_names_in_image:
            if name not in processed_players:
                unique_new_names.append(name)
                processed_players.add(name) # Mark as seen

        # Only run the API fetch for names we haven't seen yet
        if not unique_new_names:
            print("  (No new unique players found in this screenshot)")
            continue
        
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            for result in executor.map(fetch_single_player_stats, unique_new_names):
                if result:
                    # High skill alert logic
                    if result['kd'] >= GOD_SKILL_THRESHOLD:
                        status_icon = "👑 [GOD-TIER PLAYER]"
                        total_god += 1
                    elif result['kd'] >= ELITE_SKILL_THRESHOLD:
                        status_icon = "💀 [ELITE PLAYER]"
                        total_elite += 1
                    elif result['kd'] >= HIGH_SKILL_THRESHOLD:
                        status_icon = "🤓 [GOOD PLAYER]"
                        total_good += 1
                    elif result['kd'] <= LOW_SKILL_THRESHOLD:
                        status_icon = "🤖 [BOT PLAYER]"
                        total_bad += 1
                    else:
                        status_icon = "✅ [AVERAGE PLAYER]"
                        total_avg += 1
                    top_perc = est_top_percent(result['kd'])
                    # Color code based on top_perc (smaller % = flashier/better)
                    if top_perc <= 10:
                        color = "\033[95m"  # Magenta
                    elif top_perc <= 30:
                        color = "\033[91m"  # Red
                    elif top_perc <= 50:
                        color = "\033[92m"  # Green
                    else:
                        color = "\033[38;5;252m"  # Pale gray for low skill
                    reset = "\033[0m"
                    
                    print(f"{color} {status_icon:<18} {result['name']:<22} | K/D: {result['kd']:.2f} | Top {top_perc:.1f}%{reset}")
                    
                    grand_total_kd += result['kd']
                    grand_total_win += result['win']
                    total_players += 1

    print("\n" + "="*50)
    if total_players > 0:
        print(f"FINAL FOLDER STATS ({total_players} Players)")
        print(f"Folder Avg K/D: {grand_total_kd / total_players:.2f}")
        print(f"Folder Avg Winrate: {grand_total_win / total_players:.2f}%")
        print(f"GOD-TIER Players: {total_god} | Elite Players: {total_elite} | Good Players: {total_good} | Average Players: {total_avg} | Bot Players: {total_bad}")
        

        god_top_pct = est_top_percent(GOD_SKILL_THRESHOLD)
        elite_top_pct = est_top_percent(ELITE_SKILL_THRESHOLD)
        high_top_pct = est_top_percent(HIGH_SKILL_THRESHOLD)
        low_top_pct = 50.0

        expected_god_pct = god_top_pct
        expected_elite_pct = max(0.0, elite_top_pct - god_top_pct)
        expected_high_only_pct = max(0.0, high_top_pct - elite_top_pct)
        expected_average_pct = max(0.0, low_top_pct - high_top_pct)
        expected_bad_pct = max(0.0, 100.0 - low_top_pct)

        exp_god_cnt = round(expected_god_pct/100.0 * total_players)
        exp_elite_cnt = round(expected_elite_pct/100.0 * total_players)
        exp_high_cnt = round(expected_high_only_pct/100.0 * total_players)
        exp_avg_cnt = round(expected_average_pct/100.0 * total_players)
        exp_bad_cnt = round(expected_bad_pct/100.0 * total_players)

        print("\n" + "─"*70)
        print("SKILL DISTRIBUTION ANALYSIS (Expected vs Observed)")
        print("─"*70)
        print(f"{'Tier':<12} {'Expected':<25} {'Observed':<22} {'Difference':<12}")
        print("─"*70)
        
        god_diff = total_god - exp_god_cnt
        elite_diff = total_elite - exp_elite_cnt
        high_diff = total_good - exp_high_cnt
        avg_diff = total_avg - exp_avg_cnt
        bad_diff = total_bad - exp_bad_cnt
        
        print(f"{'God':<12} {expected_god_pct:>5.1f}% (~{exp_god_cnt:>2} players)   {total_god:>5} players ({total_god/total_players*100:>5.1f}%)   {god_diff:+d} ({god_diff/total_players*100:+.1f}%)")
        print(f"{'Elite':<12} {expected_elite_pct:>5.1f}% (~{exp_elite_cnt:>2} players)   {total_elite:>5} players ({total_elite/total_players*100:>5.1f}%)   {elite_diff:+d} ({elite_diff/total_players*100:+.1f}%)")
        print(f"{'Good':<12} {expected_high_only_pct:>5.1f}% (~{exp_high_cnt:>2} players)   {total_good:>5} players ({total_good/total_players*100:>5.1f}%)   {high_diff:+d} ({high_diff/total_players*100:+.1f}%)")
        print(f"{'Average':<12} {expected_average_pct:>5.1f}% (~{exp_avg_cnt:>2} players)   {total_avg:>5} players ({total_avg/total_players*100:>5.1f}%)   {avg_diff:+d} ({avg_diff/total_players*100:+.1f}%)")
        print(f"{'Bot':<12} {expected_bad_pct:>5.1f}% (~{exp_bad_cnt:>2} players)   {total_bad:>5} players ({total_bad/total_players*100:>5.1f}%)   {bad_diff:+d} ({bad_diff/total_players*100:+.1f}%)")
        print("─"*70)
    else:
        print("No player data found.")
    print("="*50)

if __name__ == "__main__":
    process_all_screenshots(TARGET_FOLDER)
