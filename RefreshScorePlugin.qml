import QtQuick 2.0
import MuseScore 3.0

MuseScore {
      menuPath: "Plugins.pluginName"
      requiresScore: false
      version: "1.0"
      onRun: {
            // TODO: Don't hardcode file path
            var score = curScore
            var scorePath = "C:/Users/Remy/Documents/DrumScoringPrototype/DrumScore.mscx"

            if (score)
            {
                  console.log("Closing score.")
                  closeScore(score)
            }            

            console.log("Opening score.")
            score = readScore(scorePath);

            Qt.quit()
            }
      }
