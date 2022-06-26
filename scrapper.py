from selenium.common.exceptions import TimeoutException
from selenium import webdriver;
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import selenium.webdriver.support.expected_conditions as EC
from pyvirtualdisplay import Display
from tqdm import tqdm
import time
import re
import platform
import os
import json
import argparse
import imageio

executable_path = "chrome-driver/chromedriver.exe" if re.search("Windows", platform.platform())\
    else "chrome-driver/chromedriver"


display = None  # contains the display used on the server
chrome_options = webdriver.ChromeOptions()

chrome_service = Service(executable_path=executable_path)

# Incognito is always set on a local Windows machines
if re.search("Windows", platform.platform()):
    chrome_options.add_argument("--incognito")
else:
    display = Display(visible=False, size=(1024, 768))
    display.start()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--remote-debugging-port=9222")

driver = webdriver.Chrome(service=chrome_service, options=chrome_options)


def search_for_item_from_homepage(web_driver, value):
    """
    Makes a test search to move the duckduckgo search bar to the top of the page
    :param web_driver: WebDriver
    :param value: str
    """
    print(f"Searching for {value}")
    try:
        web_driver.get("https://duckduckgo.com")
        # get the search form of the duckduckgo search engine
        search_form = WebDriverWait(web_driver, timeout=10).until(
            lambda d: d.find_element(By.ID, "search_form_input_homepage")
        )
        search_form.click()
        search_form.send_keys(value)  # enter search
        search_form.send_keys(Keys.RETURN)

        return True
    except Exception as ex:
        print(ex)

        return False


def search_for_item(web_driver, value):
    try:
        # get the search form of the duckduckgo search engine
        search_form = WebDriverWait(web_driver, timeout=15).until(
            lambda d: web_driver.find_element(By.ID, "search_form_input")
        )
        # search_form.click()
        try:
            search_form.clear()
        except:
            pass
        search_form.send_keys(value)  # enter search
        search_form.send_keys(Keys.RETURN)

        search_form = WebDriverWait(web_driver, timeout=15).until(
            lambda d: web_driver.find_element(By.ID, "search_form_input")
        )

        search_val = search_form.get_attribute("value")
        print(f"New search Value: {search_val}")
        return search_val == value
    except Exception as ex:
        print(ex)

        return False


def turn_off_search_moderation(web_driver):
    try:
        filter_menu = WebDriverWait(web_driver, timeout=15).until(
            lambda d: web_driver.find_element(By.XPATH,
                "/html/body/div[2]/div[5]/div[3]/div/div[1]/div[1]/div/div[2]/a"))
        filter_menu.click()
        off_option = WebDriverWait(web_driver, timeout=15).until(
            lambda d: web_driver.find_element(By.XPATH,
                "/html/body/div[6]/div[2]/div/div/ol/li[3]/a"))
        off_option.click()
        res = WebDriverWait(web_driver, timeout=15).until(
            lambda d: web_driver.find_element(By.XPATH,
                "/html/body/div[2]/div[5]/div[3]/div/div[1]/div[1]/div/div[2]/a"
            ).text == "Safe Search: Off"
        )
        if res:
            print("Safe search Moderation off")
        while not res:
            print("Retrying safe search turn off")

        return True
    except Exception as ex:
        print(ex)

        return False


def select_image_tab(web_driver):
    time.sleep(1)
    try:
        duckbar = WebDriverWait(web_driver, timeout=15).until(
            lambda d: web_driver.find_element(By.ID, "duckbar_static")
        )
        items = WebDriverWait(duckbar, timeout=15).until(
            lambda d: duckbar.find_elements(By.CLASS_NAME, "zcm__link")
        )
        time.sleep(1)
        for list_item in items:
            if list_item.text == "Images":
                list_item
                list_item.click()
                break

        # verify that the active tab element in #duckbar_static is "Images"
        duckbar = WebDriverWait(web_driver, timeout=15).until(
            lambda d: web_driver.find_element(By.ID, "duckbar_static")
        )
        active_tab = WebDriverWait(web_driver, timeout=10).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "is-active"))
        )
        return active_tab.text == "Images"
    except Exception as ex:
        print(ex)

        return False


def set_image_size(web_driver, image_size = "Large"):
    try:
        size_dropdown = WebDriverWait(web_driver, timeout=15).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "dropdown--size"))
        )
        size_dropdown.click()  # open modal dropdown
        time.sleep(2)
        modal_dropdown = WebDriverWait(web_driver, timeout=15).until(
            lambda d: web_driver.find_element(By.CLASS_NAME, "modal__list")
        )
        anchor_elements = WebDriverWait(modal_dropdown, timeout=15).until(
            lambda d: modal_dropdown.find_elements(By.TAG_NAME, "a")
        )

        # Makes sure the modal dropdown is displayed before attempting to continue
        while not modal_dropdown.is_displayed():
            time.sleep(0.2)

        for anchor_element in anchor_elements:
            print(f"anchor_element.text : {anchor_element.text}")
            if anchor_element.text == image_size:
                print(f"Size of photos set to {image_size}")
                anchor_element.click()
                break
        # This sleep is necessary since the window needs to refresh to update images with the new
        # changes that come with changing the flag in question
        time.sleep(2)

        size_dropdown = WebDriverWait(web_driver, timeout=15).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "dropdown--size"))
        )

        return size_dropdown.text == image_size
    except Exception as ex:
        print(ex)

        return False


def set_image_type(web_driver, image_type = "Photograph"):
    try:
        type_dropdown = WebDriverWait(web_driver, timeout=15).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "dropdown--type"))
        )
        type_dropdown.click()  # open the modal
        time.sleep(1)
        anchor_elements = web_driver.find_elements(By.CLASS_NAME, "js-dropdown-items")

        # Makes sure the type dropdown is displayed before attempting to continue
        while not type_dropdown.is_displayed():
            time.sleep(0.2)

        for anchor_element in anchor_elements:
            if anchor_element.text == image_type:
                print(f"Type of image set to: {image_type}")
                anchor_element.click()
                break
        # This sleep is necessary since the window needs to refresh to update images with the new
        # changes that come with changing the flag in question
        time.sleep(2)

        type_dropdown = WebDriverWait(web_driver, timeout=15).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "dropdown--type"))
        )

        return type_dropdown.text == image_type
    except Exception as ex:
        print(ex)

        return False  # signal that it was unable to select the image type


# find all the drop-down tags that affect the type of images we receive


# since the search filter is already turned off, toggle the following filters:
#   - size: change to "Medium" -> dropdown--size
#   - type: Photograph (to avoid accidental GIFs along the automated search) -> dropdown--type
def set_moderation(web_driver, moderation_type):
    try:
        filter_dropdown = WebDriverWait(web_driver, 15).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "dropdown--safe-search"))
        )
        filter_dropdown.click()
        modal_list = WebDriverWait(web_driver, timeout=15).until(
            lambda d: web_driver.find_element(By.CLASS_NAME, "modal__list")
        )
        anchor_elements = modal_list.find_elements(By.TAG_NAME, "a")

        # Makes sure the modal list is displayed before attempting to continue
        while not modal_list.is_displayed():
            time.sleep(0.2)

        for anchor_element in anchor_elements:
            print(f"anchor_element {anchor_element.text}")
            if re.search(moderation_type, anchor_element.text):
                anchor_element.click()
                print(f"SafeSearch set to: {moderation_type}")
                break
        # This sleep is necessary since the window needs to refresh to update images with the new
        # changes that come with changing the flag in question
        time.sleep(2)

        filter_dropdown = WebDriverWait(web_driver, 15).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "dropdown--safe-search"))
        )

        if moderation_type == "Off":
            return filter_dropdown.text == "Safe search: off"
        elif moderation_type == "Moderate":
            return filter_dropdown.text == "Safe search: moderate"
        elif moderation_type == "Strict":
            return filter_dropdown.text == "Safe search: strict"

    except Exception as ex:
        print(ex)

        return False


def select_first_image(web_driver):
    try:
        image_tile = WebDriverWait(web_driver, timeout=15).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "tile--img"))
        )
        image_tile.click()  # clicks on the first image

        return True
    except Exception as ex:
        print(ex)

        return False  # unable to select the image


def get_selected_image_link(web_driver, is_first_image):
    time.sleep(1)
    if is_first_image:
        try:
            selected_image_desc = WebDriverWait(web_driver, timeout=15).until(
                EC.visibility_of_element_located((By.CLASS_NAME, "c-detail__desc"))
            )
            # scroll image into view
            web_driver.execute_script("arguments[0].scrollIntoView", selected_image_desc)
        except TimeoutException as te:
            print(f"{te.__class__.__name__}: Unable to scroll in the selected image into view")
        except Exception as ex:
            print(f"{ex.__class__.__name__}: Unable to scroll in the selected image into view")

        try:
            anchor_tag = WebDriverWait(web_driver, 15).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "c-detail__btn")))
            image_href = anchor_tag.get_attribute("href")

            return image_href
        except TimeoutException as ex:
            print(f"{ex.__class__.__name__}: Unable to fetch \"href\" attr of selected image")

            return ""
        except Exception as tex:
            print(f"{tex.__class__.__name__}: Unable to fetch \"href\" attr of selected image")

            return ""
    else:
        try:
            # The details pane contains three panes at all times unless it is the first image that
            # has been selected. In this panes,it is advised to select all panes and just pick
            # out for yourself the center pane `1` (index) which contains the actively displayed image
            anchor_tag = web_driver.find_elements(By.CLASS_NAME, "c-detail__btn")
            image_href = anchor_tag[1].get_attribute("href")

            return image_href
        except TimeoutException as ex:
            print(f"{ex.__class__.__name__}: Unable to fetch \"href\" attr of selected image")

            return ""  # shows that the image was not found
        except Exception as xp:
            print(f"{xp.__class__.__name__}: Unable to fetch \"href\"")

            return "" # image was not found


def move_to_next_image(web_driver):
    try:
        next_image = WebDriverWait(web_driver, 15).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "js-detail-next"))
        )
        next_image.click()

        return True
    except Exception as ex:
        print(ex)

        return False


def dismiss_add_to_chrome_badge(web_driver):
    time.sleep(1)
    try:
        badge_link = WebDriverWait(web_driver, 15).until(
            lambda d: web_driver.find_element(By.CLASS_NAME, "badge-link")
        )

        if badge_link.is_displayed():
            badge_link_dismiss = WebDriverWait(web_driver, 15).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "js-badge-link-dismiss"))
            )
            badge_link_dismiss.click()

        return True
    except Exception as ex:
        print(ex)
        return True  # this is not an integral part of the scrapping


def download_images(web_driver, search_value, target_location, limit, export_images):
    search_for_item(web_driver, search_value)

    time.sleep(3)

    for retry_attempt in range(10):
        # We give this whole exercise 10 attempts, if by the 10th it hasnt
        # happened, we deem it as an unsuccessful search and proceed to the
        # next one
        first_image_selected = select_first_image(driver)

        if first_image_selected:
            break

        if retry_attempt == 9:
            print(f"Unable to select_first_image for: {search_value}")
            # Break out since selection was not possible
            return

    # tries to run the whole thing like a graph
    search_action_graph = [
        get_selected_image_link,
        move_to_next_image,
    ]

    link_list = []  # stores all the collected links in while scrapping the category

    # createa a flag to monitor whether the process failed somewhere in between,
    # an example where attempts to move to the next image continouosly fail, this
    # means that the problem is probably the webpage reloaded
    is_successful = True

    # context manager for a 600 image file size
    with tqdm(total=limit) as progress_bar:
        # determines whether a click() action will be performed before the
        # scrapping link starts
        is_first_image = True 

        while len(link_list) < limit and is_successful:
            # fetching the first image requires a slightly different process so we have to confirm
            # whether it is the fist image or not
            for action in search_action_graph:
                if action.__name__ == "get_selected_image_link":
                    img_link = action(web_driver, is_first_image)

                    # check whether the image img_link is empty string as this is 
                    # leading to errors in the second image
                    if img_link:
                        link_list.append(img_link)
                        progress_bar.update(1)  # update progress with new image
                    else:
                        # There is an index out of range problem (probably)
                        # and it would just be better to terminate this search
                        # rather than continue in an endless loop
                        is_successful = False
                        break

                    if is_first_image:  # the first image has now already been clicked
                        is_first_image = False
                else:
                    is_success = False
                    # Retry getting the image thrice, if no success, break out
                    # of the loop and move to the next category, we will try to recover
                    # later on
                    retry_count = 0
                    while not is_success:
                        if retry_count < 10:
                            is_success = action(web_driver)
                            retry_count += 1
                        else:
                            is_successful = False
                            break
                        
    # we only export the images if the process did not fail somewhere in
    # between
    if is_successful:
        # instead of maintaining a list which may increase the amount of memory needed to eun the program for excessively
        # large lists, it was opted to create a data dir and the search_keyword.txt file after the function continues
        # executing
        # dump all the links into a file before proceeding
        export_scrapped_links(link_list, target_location)

        if export_images:
            export_scrapped_images(link_list, target_location)
    else:
        print(f"Unable to fetch images for: {search_value}")


# this method is used to remove the '/' substr that may confuse the compiler to thinking that we are going a sub
# directory deeper. This substr is replaced with " "
def normalize_str(input_str):
    if "/" in input_str:
        return input_str.replace("/", " ")

    return input_str


def export_scrapped_links(image_links, target_location):
    data = ""
    for image_link in image_links:
        data += f"{image_link}\n"
    
    # Images are either saved in the "neutral-data" folder or the "data"
    # based on the image_type
    link_file = open(target_location, "w")

    link_file.write(data)
    link_file.close()

def export_scrapped_images(image_links, target_location):
    print("Exporting image_links: ")

    output_dir = target_location.replace(".txt", "")
    if not (os.path.exists(output_dir) and os.path.isdir(output_dir)):
        try:
            os.makedirs(output_dir)
        except Exception as e:
            print(e)

    for i, image_link in enumerate(image_links):
        try:
            image_bytes = imageio.v3.imread(image_link)
            with open(f"{output_dir}/image_{i}.jpg", "w") as image_file:
                imageio.imwrite(
                    image_file, image_bytes,
                    plugin="pillow", format="JPEG",
                )
        except Exception as e:
            print(e)


def get_output_location(input_file, config_arr):
    category, output_filename, limit = config_arr

    # each category is in the format:
    # [search_string: str, output_filename: str, limit: int]
    search_term = f"{category} pictures"
    split_dirs = input_file.split("/")
    out_location = ""

    # Generate the output directory
    for i in range(len(split_dirs)):
        # This is to allow for the same files in the same path as the
        # project to still be made into directories
        if i == 0 and len(split_dirs) > 1:
            out_location = split_dirs[0]
            continue
    
        if i != len(split_dirs) - 1:
            out_location += f"/{split_dirs[i]}"

    # Result will be stored in the /out directory
    # To cater for same directory files, we need to make sure that the
    # out_location string is not an empty string
    out_location += "/out" if out_location != "" else "out"
    # Make sure the out dir exists before trying to pass the location
    if not os.path.exists(out_location):
        try:
            os.makedirs(out_location)
        except:
            pass

    out_location += f"/{output_filename}.txt"

    return out_location, out_location.replace(".txt", "")



def attempt_recovery(input_file):
    remaining_list = []

    with open(input_file, "r", encoding="utf8") as open_input_file:
        initial_list = json.loads(open_input_file.read())
        print(f"initial list: {len(initial_list)}")

        for item in initial_list:
            try:
                txt_file, out_dir = get_output_location(input_file, item)
                out_dir_exists = os.path.exists(out_dir)
                out_dir_has_children = False
                if out_dir_exists:
                   out_dir_has_children = len(os.listdir(out_dir)) > 0
                
                # We only check if the images are there:
                if not out_dir_has_children:
                    # this means that the object has not been properly scrapped
                    # thus can be added to the list
                    remaining_list.append(item)
            except:
                pass

    return remaining_list


def fetch_images(web_driver, input_file, export_images):
    # By default atemt of recovery is tried
    remaining_categories = attempt_recovery(input_file)
    print(f"remaining searches are: {len(remaining_categories)}")
    
    for category, output_filename, limit in remaining_categories:
        # each category is in the format:
        # [search_string: str, output_filename: str, limit: int]
        search_term = f"{category} pictures"
        split_dirs = input_file.split("/")
        out_location = ""

        # Generate the output directory
        for i in range(len(split_dirs)):
            # This is to allow for the same files in the same path as the
            # project to still be made into directories
            if i == 0 and len(split_dirs) > 1:
                out_location = split_dirs[0]
                continue
        
            if i != len(split_dirs) - 1:
                out_location += f"/{split_dirs[i]}"

        # Result will be stored in the /out directory
        # To cater for same directory files, we need to make sure that the
        # out_location string is not an empty string
        out_location += "/out" if out_location != "" else "out"
        # Make sure the out dir exists before trying to pass the location
        if not os.path.exists(out_location):
            try:
                os.makedirs(out_location)
            except:
                pass

        out_location += f"/{output_filename}.txt"
        download_images(web_driver, search_term, out_location, limit, export_images)


if __name__ == "__main__":
    # Declare all the arguments required for the program to run,
    arg_parser = argparse.ArgumentParser(description="Processing search parameters")
    arg_parser.add_argument(
        "-i", "--input", type=str,
        help="""This is the absolute location of the input json file containing
        the search filters to be used in an array
        Once the images are downloaded, they are stored in the same directory
        as the input file that was created.
        """
    )
    arg_parser.add_argument(
        "-s", "--search", type=str, help="Search parameter to be used to search for images",
    )
    arg_parser.add_argument(
        "-l", "--limit", type=int, help="Number of images to be downloaded from the category",
    )
    arg_parser.add_argument(
        "-ssf", "--safe-search-filter",
        help="""The safe search filter options to be used:
        - Strict - this means that the safe search is set to strict
        - Moderate - this means that the safe search filter is set to moderate
        - Off - this turns off the safe search filter
        """,
    )
    arg_parser.add_argument(
        "-is", "--image-size",
        help="""The size of images to be downloaded. These are the are from the category:
        - Small - smaller image size
        - Medium - medium image size
        - Large - size of the image is large
        - Wallpaper- size is extremely large
        """
    )
    arg_parser.add_argument(
        "-it", "--image-type",
        help="""This is type of images to be downloaded:
        Photograph, Clipart, Transparent
        """
    )
    arg_parser.add_argument(
        "-e", "--export-images",
        action="store_true", help="""This is a variable that dictates whether
        the web scrapper would export the images as image files after scrapping the links
        """
    )

    # Fetch all the flags used to operate this program
    args = arg_parser.parse_args()
    image_type = args.safe_search_filter

    # Fetch all the arguments
    search_for_item_from_homepage(driver, "Test Search")

    time.sleep(3)
    # set up the configuration to allow for explicit images to be shown
    config_graph = [
        dismiss_add_to_chrome_badge,
        select_image_tab,
        set_moderation,
        set_image_size,
        set_image_type,
    ]

    for i, func in enumerate(config_graph):
        time.sleep(3)  # this allows the window time to refresh
        print(f"Step: {i}, func: {func.__name__}")
        if func.__name__ == "set_moderation":
            # if the content moderation is for neutral images, then the duckduckgo search engine is
            # set to "Strict" to narrow the chances of fetching explicit images to nearly 0.0
            if image_type is not None:
                func(driver, image_type)
        elif func.__name__ == "dismiss_add_to_chrome_badge" or func.__name__ == "select_image_tab":
            success = False
            while not success:
                success = func(driver)
        else:
            second_arg = None
            if func.__name__ == "set_image_size":
                second_arg = args.image_size if args.image_size is not None else "Large"
            elif func.__name__ == "set_image_type":
                second_arg = args.image_type if args.image_type is not None else "Photograph"
            
            # Recurse until option is set to required second_arg
            success = False
            while not success:
                success = func(driver, second_arg)
    
    fetch_images(
        driver, args.input,
        args.export_images if args.export_images else False,
    )

    driver.quit()
    # if running on the server, close the virtual display
    if display:
        display.stop()
