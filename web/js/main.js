const fetch_data = async () => {
    let search_word = $("#search_word").val();
    if (!search_word) {
        alert("検索ワードを入力してください。");
        return;
    }
    else {
        document.getElementById('input-group-button-right').hidden = true;
        document.getElementById('loading_button').hidden = false;
        await eel.fetch_data(search_word = search_word);
        // if (result) {
        //     document.getElementById('input-group-button-right').hidden = false;
        //     document.getElementById('loading_button').hidden = true;
        // }
        // document.getElementById('input-group-button-right').hidden = false;
        // document.getElementById('loading_button').hidden = true;
    }
}

eel.expose(output_oder_list)
function output_oder_list(text) {
    let output_text = $("#output-data").val() + text + "\n";
    $("#output-data").val(output_text);
    $("#output-data").scrollTop($("#output-data")[0].scrollHeight);
}

// eel.expose(reset_object)
// function reset_object() {
//     document.order_form.reset();
// }


eel.expose(alert_js)
function alert_js(text) {
    alert(text);
}