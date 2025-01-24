import ltk

(
    ltk.VBox(
        ltk.HBox(
            ltk.Text("Hello"),
            ltk.Button(
                "World", lambda event: ltk.find(".ltk-button, a").css("color", "green")
            ).css("color", "blue"),
        )
    ).appendTo(ltk.window.document.body)
)
