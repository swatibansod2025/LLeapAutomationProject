# ==============================
# IMPORTS
# ==============================
import time
import logging
import re

from pywinauto import Application, Desktop, mouse
from pywinauto.controls.uia_controls import TabControlWrapper
from pywinauto.controls.uiawrapper import UIAWrapper
from pywinauto.application import WindowSpecification
from pywinauto.findwindows import ElementNotFoundError
from pywinauto.keyboard import send_keys
from time import sleep
import os
import time
import fnmatch
from pywinauto import timings
from pywinauto.timings import wait_until_passes
from pywinauto.timings import wait_until

# ==============================
# SINGLETONS (CRITICAL)
# ==============================

_UIA_APP = None
_UIA_WINDOWS = {}
_APPIUM_LIB = None

# ==============================
# CORE HELPERS
# ==============================


def get_uia_window(title_re, timeout=15):
    """Get cached pywinauto window (connect only once)."""
    global _UIA_APP, _UIA_WINDOWS

    if title_re in _UIA_WINDOWS:
        return _UIA_WINDOWS[title_re]

    if _UIA_APP is None:
        _UIA_APP = Application(backend="uia").connect(title_re=title_re, timeout=timeout)

    window = _UIA_APP.window(title_re=title_re)
    window.wait("exists visible ready", timeout=timeout)

    _UIA_WINDOWS[title_re] = window
    return window

def normalize_window(window_or_title):
    """Normalize input into a ready pywinauto window."""
    if isinstance(window_or_title, (str, re.Pattern)):
        window = get_uia_window(window_or_title)
    elif isinstance(window_or_title, WindowSpecification):
        window = window_or_title
    elif isinstance(window_or_title, UIAWrapper):
        app = Application(backend="uia").connect(process=window_or_title.process_id())
        window = app.window(handle=window_or_title.handle)
    else:
        raise TypeError(f"Unsupported window type: {type(window_or_title)}")

    if window.is_minimized():
        window.restore()

    return window

def safe_click(element, use_mouse=False):
    """Prefer UIA invoke, fallback to mouse."""
    element.wait("visible enabled ready", timeout=10)
    try:
        if use_mouse:
            element.click_input()
        else:
            element.invoke()
    except Exception:
        element.click_input()

def click_element_by_xpath_in_window(window_or_title, xpath, timeout=10, use_mouse=False):
    """
    Click an element inside a given window using a WinAppDriver-style XPath.
    This is a pywinauto implementation (NO Appium).

    Supported XPath patterns:
      //*[@AutomationId='id']
      //*[@Name='text']
      //*[@ControlType='Button']
      //*[contains(@Name,'text')]
      Combined attributes with 'and'

    :param window_or_title: Window title, regex, or pywinauto window
    :param xpath: XPath string
    :param timeout: wait timeout
    :param use_mouse: force mouse click
    """

    window = normalize_window(window_or_title)

    # ---------- Parse XPath ----------
    auto_id = None
    name = None
    control_type = None
    name_contains = None

    # AutomationId
    m = re.search(r"@AutomationId\s*=\s*'([^']+)'", xpath)
    if m:
        auto_id = m.group(1)

    # Name exact
    m = re.search(r"@Name\s*=\s*'([^']+)'", xpath)
    if m:
        name = m.group(1)

    # Name contains
    m = re.search(r"contains\s*\(\s*@Name\s*,\s*'([^']+)'\s*\)", xpath)
    if m:
        name_contains = m.group(1)

    # ControlType
    m = re.search(r"@ControlType\s*=\s*'([^']+)'", xpath)
    if m:
        control_type = m.group(1)

    # ---------- Locate element ----------
    if auto_id:
        elem = window.child_window(auto_id=auto_id, control_type=control_type)
    elif name:
        elem = window.child_window(title=name, control_type=control_type)
    elif name_contains:
        # fallback: search descendants
        for e in window.descendants(control_type=control_type):
            if name_contains.lower() in e.window_text().lower():
                elem = e
                break
        else:
            raise ElementNotFoundError(f"No element contains Name '{name_contains}'")
    else:
        raise ValueError(f"Unsupported XPath: {xpath}")

    # ---------- Click ----------
    elem.wait("exists visible enabled ready", timeout=timeout)
    safe_click(elem, use_mouse=use_mouse) 

def click_element_by_partial_name_help_automationid(window_or_title, partial_text, control_type=None, timeout=5):
    """
    Click the first element where Name, HelpText, or AutomationId contains `partial_text`.
    Does NOT scroll the element. Optimized for your existing method style.

    Args:
        window_or_title: Window title, regex, or pywinauto WindowSpecification/UIAWrapper
        partial_text: Substring to match in Name, HelpText, or AutomationId
        control_type: Optional control type filter (e.g., "Text", "Button")
        timeout: How long to wait for element to appear

    Raises:
        Exception if no matching element is found
    """
    window = normalize_window(window_or_title)
    partial_text_lower = str(partial_text).lower()
    end_time = time.time() + timeout

    while time.time() < end_time:
        for elem in window.descendants(control_type=control_type):
            try:
                name = elem.window_text() or ""
                help_text = getattr(elem, "help_text", "") or ""
                auto_id = getattr(elem, "automation_id", "") or ""

                if (partial_text_lower in name.lower() or
                    partial_text_lower in help_text.lower() or
                    partial_text_lower in auto_id.lower()):
                    
                    wait_for_visible(elem, timeout=1)
                    safe_click(elem)
                    print(f"Clicked element matching '{partial_text}'")
                    return
            except Exception:
                continue
        time.sleep(0.2)

    raise Exception(f"No element found matching partial text '{partial_text}'")

def maximize_window_by_title(window_or_title, timeout=10, wait_time=0.5):
    """
    Reliably maximize a window by title or regex.
    Uses keyboard fallback for WPF / custom apps.
    """
    window = normalize_window(window_or_title)

    end_time = time.time() + timeout
    while time.time() < end_time:
        try:
            if window.exists():
                break
        except Exception:
            pass
        time.sleep(0.2)
    else:
        raise Exception(f"Window '{window_or_title}' not found within {timeout}s")

    # Restore if minimized
    if window.is_minimized():
        window.restore()
        time.sleep(0.3)

    # Bring to foreground
    try:
        window.set_focus()
    except Exception:
        # Some apps block set_focus, fallback
        pass
    time.sleep(0.2)

    # Try UIA maximize
    try:
        if not window.is_maximized():
            window.maximize()
            time.sleep(0.5)
    except Exception:
        pass

    # HARD fallback – keyboard
    if not window.is_maximized():
        send_keys('{VK_LWIN down}{UP}{VK_LWIN up}')
        time.sleep(wait_time)

    if not window.is_maximized():
        raise Exception(f"Window '{window.window_text()}' did not maximize")

    return window


# ==============================
# BASIC UIA ACTIONS
# ==============================

def click_element_using_automation_id(window_or_title, automation_id, timeout=5):
    """
    Click the first element matching the given automation_id in the window.
    """
    window = normalize_window(window_or_title)
    
    # Pick the first element with found_index=0
    elem = window.child_window(auto_id=automation_id, found_index=0)
    
    # Wait until it is visible and enabled
    elem.wait("visible enabled ready", timeout=timeout)
    
    # Click safely
    safe_click(elem)

def click_child_element_by_name(
    window_title,
    child_name,
    child_control_type=None,
    wait_time=0.2,
    timeout=5,
    retry_interval=0.2,
):
    """
    Click a child element safely with a wait/retry mechanism.
    """

    window = normalize_window(window_title)

    # Build search kwargs safely
    search_kwargs = {"title": child_name}
    if child_control_type:
        search_kwargs["control_type"] = child_control_type

    child = window.child_window(**search_kwargs)

    try:
        # Wait for existence (NOT wrapper yet)
        wait_until(
            timeout,
            retry_interval,
            lambda: child.exists(timeout=0)
        )

        # Wait until it is ready for input
        child.wait("visible enabled ready", timeout=timeout)

    except TimeoutError:
        raise Exception(
            f"Child element '{child_name}' not found or not ready in window '{window_title}'"
        )

    # Click
    child.click_input()
    time.sleep(float(wait_time))
    
    
def click_and_verify_disabled(window_title, automation_id, wait_time=0.5):
    window = normalize_window(window_title)
    button = window.child_window(auto_id=automation_id, control_type="Button")
    safe_click(button)
    time.sleep(wait_time)
    return not button.is_enabled()

def click_element_in_tile(window, text, retries=3, delay=1):
    """
    Click a button in a simulator tile by its child element text.

    Args:
        window: pywinauto window object
        text: text to match in child elements
        retries: number of times to retry if element not found
        delay: delay between retries in seconds
    """
    for attempt in range(1, retries + 1):
        try:
            for btn in window.descendants(control_type="Button"):
                # Check if any child of this button has the target text
                if any(child.window_text() == text for child in btn.descendants()):
                    btn.click_input()
                    print(f"Clicked simulator tile: {text}")
                    return
            raise ElementNotFoundError(f"Simulator tile '{text}' not found")
        except ElementNotFoundError as e:
            if attempt < retries:
                print(f"{e}, retrying in {delay} seconds... (Attempt {attempt}/{retries})")
                sleep(delay)
            else:
                raise
        except Exception as e:
            # Catch unexpected errors, log, but don't fail silently
            print(f"Unexpected error while clicking '{text}': {e}")
            raise
           
def connect_to_running_app(window_title_regex, backend="uia", timeout=10):
    """
    Connect to an already running application by its window title (regex supported)
    and focus the main window.

    :param window_title_regex: Regex pattern to match the window title
    :param backend: pywinauto backend to use (default: "uia")
    :param timeout: Timeout in seconds for window to become ready
    :return: pywinauto WindowSpecification object
    :raises Exception: If connection or window focus fails
    """
    try:
        # Connect to the running application
        app = Application(backend=backend).connect(title_re=window_title_regex, timeout=timeout)

        # Get the main/top window
        window = app.window(title_re=window_title_regex)
        window.wait("exists enabled visible ready", timeout=timeout)

        # Ensure the window is focused
        window.set_focus()
        logging.info(f"Connected and focused window matching title regex: '{window_title_regex}'")
        return window

    except Exception as e:
        logging.error(f"Failed to connect to running app with title regex '{window_title_regex}': {e}", exc_info=True)
        raise

def click_on_a_option_from_context_menu(option_name, timeout=12):
    """
    Click WPF context menu item using LegacyIAccessible.Name
    """

    desktop = Desktop(backend="uia")
    end_time = time.time() + timeout

    while time.time() < end_time:
        for w in desktop.windows():
            try:
                if not w.is_visible():
                    continue

                for e in w.descendants():
                    try:
                        legacy = getattr(e, "iface_legacy_iaccessible", None)
                        if not legacy:
                            continue

                        text = legacy.CurrentName.strip()
                        if option_name.lower() in text.lower():
                            e.click_input()
                            time.sleep(0.3)
                            return
                    except Exception:
                        continue
            except Exception:
                continue

        time.sleep(0.4)

    raise Exception(
        f"Context menu option '{option_name}' not found via LegacyIAccessible after {timeout} seconds"
    )

def verify_report_file_present(directory_path, file_prefix, timeout=300, folder_wait=10, initial_wait=2):
    """
    Wait until the folder exists, then verify that a report file starting
    with the given prefix exists in the specified directory.

    :param directory_path: Folder path
    :param file_prefix: File name prefix to match
    :param timeout: Max wait time in seconds for the file
    :param folder_wait: Max wait time in seconds for the folder to appear
    :param initial_wait: Initial pause before checking files
    :return: Full path to the found file
    :raises AssertionError: If the folder or file is not found
    """

    # Wait for the folder to exist
    end_folder_wait = time.time() + folder_wait
    while time.time() < end_folder_wait:
        if os.path.exists(directory_path) and os.path.isdir(directory_path):
            break
        time.sleep(0.5)
    else:
        raise AssertionError(f"Folder '{directory_path}' not found after {folder_wait} seconds")

    # Optional initial wait before checking files
    if initial_wait > 0:
        time.sleep(initial_wait)

    # Wait for the file to appear
    end_time = time.time() + timeout
    pattern = f"{file_prefix}*"

    while time.time() < end_time:
        for file in os.listdir(directory_path):
            if fnmatch.fnmatch(file, pattern):
                print(f"Found report file: {file}")
                return os.path.join(directory_path, file)
        time.sleep(1)

    raise AssertionError(
        f"No file starting with '{file_prefix}' found in "
        f"'{directory_path}' within {timeout} seconds"
    )

def verify_folder_is_empty(directory_path, timeout=10):
    """
    Verify that the specified folder contains no files or subfolders.

    Args:
        directory_path: full path to the folder
        timeout: seconds to wait and re-check (optional)
    
    Raises:
        AssertionError: if any file/folder is present after timeout
    """
    import os, time

    directory_path = os.path.normpath(directory_path)
    end_time = time.time() + timeout

    print(f"Checking if folder is empty: '{directory_path}'")

    while time.time() < end_time:
        if os.path.isdir(directory_path):
            contents = os.listdir(directory_path)
            if not contents:
                print("Folder is empty ✅")
                return True
        else:
            raise AssertionError(f"Directory does not exist: {directory_path}")

        time.sleep(1)

    raise AssertionError(f"Folder is not empty: {contents}")

def right_click_element_by_name1(window_or_title, element_name, timeout=10):
    window = normalize_window(window_or_title)
    window.wait("visible ready", timeout=timeout)
    window.set_focus()

    elem = window.child_window(title=element_name)
    elem.wait("visible enabled ready", timeout=timeout)

    # Ensure element is truly clickable
    rect = elem.rectangle()
    elem.click_input(
        button="right",
        coords=(rect.width() // 2, rect.height() // 2)
    )

    time.sleep(0.5)
    
def expand_themes_if_not_expanded(window_or_title, timeout=10):
    """
    Expand 'Themes' if it is currently collapsed.
    Safe to call multiple times.
    """

    window = normalize_window(window_or_title)
    window.wait("visible ready", timeout=timeout)

    themes = window.child_window(
        title="Themes",
        auto_id="HeaderSite",
        control_type="Button"
    )
    themes.wait("visible enabled ready", timeout=timeout)

    try:
        # 0 = collapsed, 1 = expanded
        if themes.iface_toggle.CurrentToggleState == 0:
            themes.iface_toggle.Toggle()
    except Exception:
        # Fallback for rare cases (keeps consistency with safe_click style)
        safe_click(themes)

def click_theme(parent_window, theme_name):
    """
    Click a theme by name inside the 'Themes' TreeItem.
    Works with deep WindowsForms Tree structure.

    Args:
        parent_window: pywinauto WindowSpecification or UIAWrapper
        theme_name: str, the theme text to click
    """
    parent_window = normalize_window(parent_window)

    # Step 1: Find the main Tree
    trees = parent_window.descendants(control_type="Tree")
    if not trees:
        raise ValueError("No Tree controls found in window.")
    tree = trees[0]  # Assuming single Tree

    # Step 2: Find the top-level 'Themes' TreeItem
    top_items = tree.children(control_type="TreeItem")
    themes_item = None
    for item in top_items:
        if item.window_text().strip() == "Themes":
            themes_item = item
            break
    if not themes_item:
        raise ValueError("Top-level 'Themes' TreeItem not found.")

    # Step 3: Expand top-level Themes
    try:
        themes_item.expand()
    except Exception:
        pass

    # Step 4: Find second-level TreeItem with desired theme
    second_items = themes_item.descendants(control_type="TreeItem")
    target_item = None
    for ti in second_items:
        for text_elem in ti.descendants(control_type="Text"):
            if text_elem.window_text().strip() == theme_name:
                target_item = text_elem
                break
        if target_item:
            break

    if not target_item:
        raise ValueError(f"Theme '{theme_name}' not found.")

    # Step 5: Click the theme
    rect = target_item.rectangle()
    mouse.click(coords=rect.mid_point())
       
def click_button(window_or_element, button_name):
    """
    Click a button inside the given window or element.
    
    Args:
        window_or_element: main window or parent container.
        button_name (str): the name/title of the button to click (e.g., 'Close').
    """
    # Locate the button by title and control type
    button = window_or_element.child_window(
        title=button_name,
        control_type="Button"
    )
    
def click_on_button(window_or_element, button_name):
    """
    Click a button inside the given window or element.
    """
    for btn in window_or_element.descendants(control_type="Button"):
        if btn.window_text() == button_name:
            btn.click_input()
            return

    raise Exception(f"Button '{button_name}' not found")

    
    # Wait until visible and enabled
    button.wait("visible enabled", timeout=10)
    
    # Get the clickable point and click
    point = button.rectangle().mid_point()
    mouse.click(coords=(point.x, point.y))
# ==============================
# TEXT / COMBOBOX
# ==============================

def set_textbox_value(window_or_title, automation_id, value, wait_time=0.2):
    window = normalize_window(window_or_title)
    textbox = window.child_window(auto_id=automation_id, control_type="Edit")
    textbox.wait("visible enabled ready", timeout=5)
    textbox.set_edit_text(str(value))
    time.sleep(float(wait_time))

def get_element_value(window_title, automation_id):
    window = normalize_window(window_title)
    elem = window.child_window(auto_id=automation_id)
    elem.wait("visible ready", timeout=5)
    try:
        return elem.get_value()
    except Exception:
        return elem.window_text()

def is_eye_status_closed(window_or_title):
    """
    Check if the EyesComboBox is currently set to 'Closed'.
    
    Args:
        window_or_title: The window title, regex, or a WindowSpecification/UIAWrapper
    Returns:
        True if the value is 'Closed', False otherwise.
    """
    try:
        window = normalize_window(window_or_title)

        # Use child_window and element_info to avoid wrapper waits
        combo = window.child_window(
            auto_id="EyesComboBox",
            control_type="ComboBox"
        )

        elem = combo.element_info

        # Most reliable value exposed by UIA
        current_value = elem.name

        return current_value == "Closed"

    except ElementNotFoundError:
        # ComboBox not found → fail the test or return False
        return False
    except Exception:
        # Any other UIA limitation → fail-safe
        return False


def select_status_from_Eyecombobox(status):
    window = Desktop(backend="uia").window(title_re=".*Virtual SimMan.*")
    window.wait("exists ready", timeout=10)

    combo = window.child_window(
        auto_id="EyesComboBox",
        control_type="ComboBox"
    ).wrapper_object()

    combo.set_focus()
    combo.expand()
    combo.select(status)

    current_value = combo.selected_text()
    if current_value != status:
        raise Exception(f"Failed to select '{status}'")

    print(f"EyesComboBox successfully set to '{status}'")

# ==============================

# WINDOW DISCOVERY
# ==============================

def get_window_by_title(title_substring, retries=3, delay=1):
    for _ in range(retries):
        for w in Desktop(backend="uia").windows():
            try:
                if title_substring in w.window_text():
                    return w
            except Exception:
                pass
        time.sleep(delay)
    raise Exception(f"No window found with title containing '{title_substring}'")

def get_window_title_by_contained_element(element_text, retries=4, delay=2):
    """
    Return the title of the window that contains a visible element
    with the given text.
    """
    element_text = str(element_text)

    for _ in range(retries):
        for w in Desktop(backend="uia").windows():
            try:
                if not w.is_visible():
                    continue

                # Fast path: check only visible descendants
                for e in w.descendants():
                    if (
                        e.window_text() == element_text
                        and e.is_visible()
                    ):
                        return w.window_text()

            except Exception:
                continue

        time.sleep(delay)

    raise Exception(
        f"No window found containing element with text '{element_text}'"
    )

def switch_to_window_containing_element(element_text, retries=5, delay=1):
    """
    Switch to the window/dialog that contains an element with the given text.
    Optimized to reduce redundant descendant searches.
    
    :param element_text: Text of the UI element to search for (e.g. 'Local computer')
    :param retries: Number of retries
    :param delay: Delay between retries in seconds
    :return: pywinauto window object
    """
    element_text_lower = element_text.lower().strip()
    checked_handles = set()

    for attempt in range(retries):
        windows = Desktop(backend="uia").windows()

        for w in windows:
            # Skip windows already checked
            if w.handle in checked_handles:
                continue

            checked_handles.add(w.handle)

            try:
                for e in w.descendants(control_type="Text"):
                    if element_text_lower in (e.window_text() or "").lower():
                        w.set_focus()
                        print(f"Switched to window: {w.window_text()}")
                        return w   # ✅ IMMEDIATE EXIT (no more retries)
            except Exception:
                continue

        time.sleep(delay)

    raise Exception(f"No window found containing element with text '{element_text}'")

def switch_to_window_by_title_regex(title_regex, retries=3, delay=1):
    """
    Switch focus to the first window matching the given regex.

    :param title_regex: Regex pattern to match window title
    :param retries: Number of retries
    :param delay: Delay between retries in seconds
    :return: pywinauto WindowSpecification object
    """
    title_regex = str(title_regex)  # ensure string for pywinauto
    for attempt in range(1, retries + 1):
        try:
            app = Application(backend="uia").connect(title_re=title_regex)
            window = app.top_window()
            window.wait("exists visible ready", timeout=5)
            window.set_focus()
            logging.info(f"Switched to window: {window.window_text()}")
            return window
        except Exception as e:
            logging.warning(
                f"Attempt {attempt}/{retries} failed to switch to window matching '{title_regex}': {e}"
            )
            time.sleep(delay)

    raise Exception(f"No window found matching regex '{title_regex}' after {retries} attempts")

def click_element_in_window(window, name):
    """
    Click an element by its name in a specific pywinauto window.
    """
    elements = window.descendants()
    for e in elements:
        if e.window_text() == name:
            e.click_input()
            print(f"Clicked element: {name}")
            return
    raise Exception(f"Element with name '{name}' not found in window '{window.window_text()}'")

# ==============================
# SLIDERS / MOUSE ACTIONS
# ==============================


def click_at_coordinates(x, y, wait_time=0.5, window_or_title=None):
    if window_or_title:
        normalize_window(window_or_title)
    mouse.click(coords=(int(x), int(y)))
    time.sleep(wait_time)
def get_slider_value(app_title, container_control_type="Tab"):
    """
    Returns the current value of a slider, if accessible via UIA ValuePattern.

    :param app_title: Window title or regex to identify the application window
    :param container_control_type: Control type of the slider container (default: "Tab")
    :return: Slider value as float
    :raises Exception: If window cannot be accessed or ValuePattern is unavailable
    """
    try:
        # Connect to the application and normalize the window
        window = get_uia_window(app_title)

        # Find the slider container
        container = window.child_window(control_type=container_control_type)
        container.wait("visible enabled ready", timeout=10)

        # Check if ValuePattern is available
        if hasattr(container, "iface_value") and container.iface_value:
            value = container.iface_value.CurrentValue
            return float(value)  # convert to float for consistency
        else:
            raise Exception(f"ValuePattern not available for the slider ({container_control_type})")
    except Exception as e:
        logging.error(f"Failed to get slider value for window '{app_title}': {e}", exc_info=True)
        raise

def set_lung_compliance_by_value(window_or_title, value, min_val=0, max_val=100):
    """
    Set lung compliance slider by dragging to a percentage value.
    """

    window = normalize_window(window_or_title)

    # Locate the TabControl (slider container)
    slider = window.child_window(control_type="Tab")
    slider.wait("visible ready", timeout=10)

    rect = slider.rectangle()

    # Calculate X coordinate
    percentage = (value - min_val) / (max_val - min_val)
    x = int(rect.left + (rect.width() * percentage))
    y = rect.top + rect.height() // 2

    # Click + drag slightly to ensure thumb move
    mouse.press(coords=(x - 20, y))
    time.sleep(0.05)
    mouse.move(coords=(x, y))
    mouse.release(coords=(x, y))

    time.sleep(0.3)

def wait_for_visible(wrapper, timeout=10):
    end_time = time.time() + timeout
    while time.time() < end_time:
        if wrapper.is_visible():
            return True
        time.sleep(0.2)
    raise TimeoutError("Element did not become visible in time")

def set_lung_compliance_by_value_index(window_or_title,value,tab_index,min_val=0,max_val=100):
    """
    Set lung compliance slider by dragging inside the correct TabControl.

    :param tab_index: zero-based index of the TabControl (7th tab = 6)
    """
    value = int(value)
    tab_index = int(tab_index)
    min_val = int(min_val)
    max_val = int(max_val)

    window = normalize_window(window_or_title)
    window.wait("visible ready", timeout=10)

    tabs = window.descendants(control_type="Tab")
    if len(tabs) <= tab_index:
        raise IndexError(f"Requested Tab index {tab_index}, but only {len(tabs)} tabs found")

    slider = tabs[tab_index]

    wait_for_visible(slider, timeout=10)

    rect = slider.rectangle()

    percentage = (value - min_val) / (max_val - min_val)
    x = int(rect.left + rect.width() * percentage)
    y = rect.top + rect.height() // 2

    mouse.press(coords=(x - 20, y))
    time.sleep(0.05)
    mouse.move(coords=(x, y))
    mouse.release(coords=(x, y))

    time.sleep(0.3)
       
def set_lung_compliance(window_title):
    """
    Click the 'Lung Compliance' slider in the application.

    Args:
        window_or_title: Window title or regex to identify the window
    """
    time.sleep(2)  # Wait for UI to load

    # Connect to the main window
    window = Desktop(backend="uia").window(title_re=window_title)
    
    # Access the TabControl
    tab_control = window.child_window(control_type="Tab")
    
    if not tab_control.exists():
        raise Exception("TabControl not found in the main window")

    # Now search for the Lung Compliance slider inside the TabControl
    slider = None
    for elem in tab_control.descendants():
        try:
            name = elem.window_text() or ""
            help_text = getattr(elem, "help_text", "") or ""
            auto_id = getattr(elem, "automation_id", "") or ""

            if "lung compliance" in name.lower() \
               or "lung compliance" in help_text.lower() \
               or "lung compliance" in auto_id.lower():
                slider = elem
                break
        except Exception:
            continue

    if not slider:
        raise Exception("Lung Compliance slider not found inside TabControl")

    # Click the slider
    slider.click_input()
    print("Clicked Lung Compliance slider successfully")
    
# ==============================
# TABS / TOOLTIP
# ==============================

def click_tab_by_index(window_or_title, tab_index):
    window = normalize_window(window_or_title)
    tabs = window.descendants(control_type="Tab")
    tab = tabs[int(tab_index)]
    rect = tab.rectangle()
    window.click_input(coords=(rect.mid_point().x, rect.mid_point().y))

def find_tab_by_tooltip(window, tooltip_text, retries=3, delay=0.5):
    for _ in range(retries):
        for tt in Desktop(backend="uia").windows(control_type="ToolTip"):
            if tooltip_text in tt.window_text():
                pt = tt.rectangle().mid_point()
                el = window.from_point(pt)
                while el:
                    if el.friendly_class_name() == "TabControl":
                        return TabControlWrapper(el)
                    el = el.parent()
        time.sleep(delay)
    raise Exception(f"No TabControl found for tooltip '{tooltip_text}'")

# ==============================
# VERIFY / POPUPS
# ==============================
def verify_HR_value(window_or_title, timeout=5, retry_interval=0.5):
    """
    Check if the HR element shows 100 and click OK safely.
    """
    window = normalize_window(window_or_title)

    # Wait for HR element
    try:
        hr_elem = wait_until_passes(
            timeout,
            retry_interval,
            lambda: window.child_window(auto_id="11").wrapper_object()
        )
        hr_elem.click_input()
    except ElementNotFoundError:
        raise Exception("HR element with AutomationId '11' not found")

    # Wait for textbox and OK button
    try:
        text_box = wait_until_passes(
            timeout,
            retry_interval,
            lambda: window.child_window(auto_id="2093").wrapper_object()
        )
        ok_button = wait_until_passes(
            timeout,
            retry_interval,
            lambda: window.child_window(title="OK", control_type="Button").wrapper_object()
        )
    except ElementNotFoundError:
        raise Exception("Textbox or OK button not found")

    # Check the HR value
    hr_value = text_box.window_text().strip()
    ok_button.click_input()  # always click OK

    return hr_value == "100"
    
def verify_element_value(window_or_title, automation_id, expected_value, timeout=5):
    window = normalize_window(window_or_title)
    elem = window.child_window(auto_id=automation_id)
    end = time.time() + timeout
    while time.time() < end:
        if str(elem.window_text()) == str(expected_value):
            return True
        time.sleep(0.2)
    raise AssertionError(f"Expected '{expected_value}', found '{elem.window_text()}'")



