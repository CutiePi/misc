// add list of desired user ids
/** extract nameIds in console 
 * const inputs = document.getElementsByName('reviewer_user_ids[]');
let nameIds = {};
    for (let checkbox of inputs) {
        nameIds[checkbox.parentNode.getElementsByClassName('js-username')[0].outerText] = checkbox.value
        // clear all reviewers
        // checkbox.checked = false;
    }
 */
    const nameIds = {
        // "SomeUserId": "123456789", example
    };
    
    const userIds = Object.values(nameIds);
    
    
    
    const selectReviewers = () => {
        console.log('select reviewers');
        const inputs = document.getElementsByName('reviewer_user_ids[]');
    
        for (let checkbox of inputs) {
            if (userIds.includes(checkbox.value)) {
                checkbox.checked = true;
            }
            // clear all reviewers
            // checkbox.checked = false;
        }
        // trigger update
        inputs[50].click();
        inputs[50].click();
    }
    
    const closeMenu = () => {
        console.log('close menu');
        document.getElementById('reviewers-select-menu').focus();
        document.getElementById('reviewers-select-menu').childNodes[1].click();
    }
    
    console.log('open menu');
    document.getElementById('reviewers-select-menu').focus();
    // double click otherwise users don't load for some reason
    document.getElementById('reviewers-select-menu').childNodes[1].click();
    document.getElementById('reviewers-select-menu').childNodes[1].click();
    
    // wait for list to load
    setTimeout(selectReviewers, 500);
    setTimeout(closeMenu, 750);