"""
Send an email using TLS/SSL.
"""

(import sys)
(import smtplib)
(import traceback)


(defn send-exception [exc * subject]
  "Send a formatted Exception object."
  (setv tb (.join "" (.format_exception traceback :etype (type exc) :value exc :tb exc.__traceback__)))
  (send (or subject "error") tb))

(defn send [body * subject sender recipient server port password]
  "Send an email."
  (setv message f"Subject: {subject}\n\n{body}")
  (with [server (smtplib.SMTP_SSL server port)]
    (.login server sender password)
    (.sendmail server sender recipient message)))

;; TODO fix this
(defn send-file [#** kwargs]
  "Send stdin as an email.
  Use as:
    $ mail 'subject line' body
  where section is the section in the email ini file."
  (send (get sys.argv 2)
        (-> (.read sys.stdin)
            (.encode "UTF-8")
            (.decode "ASCII" "ignore"))
        #** kwargs))
