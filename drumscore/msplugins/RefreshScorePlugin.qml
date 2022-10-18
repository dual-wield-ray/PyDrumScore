import QtQuick 2.0
import MuseScore 3.0

MuseScore {
      menuPath: "Plugins.RefreshCurrentScore"
      requiresScore: true
      version: "1.0"
      onRun: {
            var score = curScore
            var scorePath = score.path
            
            console.log("Closing score '" + scorePath + "'.")
            closeScore(score)

            console.log("Reopening score.")
            readScore(scorePath)

            Qt.quit()
            }
    }
