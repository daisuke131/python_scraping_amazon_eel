const fetch_data = async () => {
    let search_word = $("#search_word").val();
    if (!search_word) {
        alert("検索ワードを入力してください。");
        return;
    }
    else {
        $("#input-group-button-right").hide();
        $("#loading_button").show();
        await eel.fetch_data(search_word = search_word);
        $("#input-group-button-right").show();
        $("#loading_button").hide();
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