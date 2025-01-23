import constants
import ltk

(
    ltk.VBox(
        ltk.HBox(
            ltk.Text(constants.OBJECTIVE_OPT_KEY),
            ltk.Button(
                "World", lambda event: ltk.find(".ltk-button, a").css("color", "green")
            ).css("color", "blue"),
        )
    ).appendTo(ltk.window.document.body)
)
