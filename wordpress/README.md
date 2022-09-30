# Wordpress-Eingabemaske für die Nachrichten-Wand

## Unterseite und Form

- Das Form ist bereits angelegt mithilfe des `WPForms`-Plugin und zu finden unter `WPForms > Nachrichten-Wand-Formular`. Die Felder `Code` und `Token` sind versteckt und nehmen automatische ihre Werte aus den entsprechenden URL-Parametern auf. (z.B. `{query_var key="code"}`).

- Die Unterseite existiert auch bereits und ist in Wordpress unter `Seiten > Mietenschmutztwitter` zu finden. Sie bindet das Nachrichten-Wand-Formular ein.

## Code Snippet Plugin

Um den Code sauber in Wordpress zu integrieren sollte das Plugin `Code Snippets` installiert werden. Dazu in Wordpress `Plugins > Installieren > Plugins durchsuchen > "Code Snippets" > Installieren` wählen. Um das System aufgeräumt  zu halten wurde das Plugin nach dem letzten Einsatz wieder deinstalliert.

## Code hinterlegen

Ist `Code Snippet` installiert erscheint im Hauptmenü von Wordpress ein neuer EIntrag `Snippets`.  Unter `Snippets > Neu Hinzufügen`kann der Code hinterlegt werden. Anschließend muss das Snippet gespeichert und aktiviert werden.

 Beide Funktionen und beide Hooks können einfach untereinander ins selbe Snippet geschrieben werden.

## Beschreibung des Codes

Der Code besteht aus zwei Funktionen, die an einen entsprechenden Hook von Wordpress gehängt werden.

- Die Funktion `redirectCodeToToken` hängt am Hook `template_redirect` der bei jedem Wordpress-Seitenaufruf ausgelöst wird und eine Weiterleitung ermöglicht. Darum muss streng gefiltert werden, dass nur bei der entsprechenden Seite eine Weiterleitung stattfindet. Die Funktion nimmt sich den Access-Code aus dem URL-Parameter `code`, holt damit ein Token von der API  ab und ergänzt das Token in einer Weiterleitung als URL--Parameter `token`.

- Die Funktion `sendingDataToAPI`hängt am Hook `wpforms_process`, der ausgelöst wird, wenn ein beliebiges Formular abgesendet wird. Darum muss streng geprüft werden dass es sich um das korrekte Formulat handelt, anhand der Formular-ID. Die Funktion sendet die eingegebenen Daten, inklusive des automatisch vorbelegten Tokens an die API um eine Nachricht an die Nachrichten-Wand abzusetzen.  

## Der Code

- `redirectCodeToToken` - Funktion:

```php
function redirectCodeToToken() {

	$url_path = $_SERVER['REQUEST_URI'];
	$url_parameters = array();
	parse_str($_SERVER['QUERY_STRING'], $url_parameters);

	if(str_starts_with($url_path, '/nachrichten-wand')) {
		if(array_key_exists('code', $url_parameters) && !array_key_exists('token', $url_parameters)) {
			$code = $url_parameters['code'];

			// Hole das Token
			$base_url = 'http://144.126.245.62:8000'; // https://dwenteignen.party
			$token_url = "$base_url/token";
			$body = "username=$code&password=$code";
			$headers = array(
				'Content-Type'			=> 'application/x-www-form-urlencoded',
			);

			$token_response = wp_remote_post( $token_url, array( 'body' => $body, 'headers' => $headers ) );
		
			// Fehlerbehandlung
			if($token_response['response']['code'] == 401) {
				exit( wp_redirect( "/nachrichten-wand-ungueltig" ) );
			}
			if($token_response['response']['code'] != 200) {
				exit( wp_redirect( "/nachrichten-wand-fehler" ) );
			}
		
			// Token extrahieren
			$token = json_decode($token_response['body'], true)['access_token'];
	
			exit( wp_redirect( "$url_path&token=$token" ) );
		}
	}
}
```

- `template_redirect` - Hook:

```php
add_action( 'template_redirect', 'redirectCodeToToken' );
```

- `sendingDataToAPI` - Funktion:

```php
function sendingDataToAPI( $fields, $entry, $form_data) {

	// Nur bei dem entsprechenden Form, identifiziert über die ID
	if ($form_data['id'] == 5446) {
		
		$base_url = 'http://144.126.245.62:8000'; // https://dwenteignen.party
		
		$name = $entry['fields']['4'];
		$text = $entry['fields']['1'];
		$code = $entry['fields']['8'];
		$token = $entry['fields']['9'];

		// Sende die Nachricht
		$message_url = "$base_url/message";
		$body = json_encode([
			'text'                  => $text,
			'name'              	=> $name,
		]);
		$headers = array(
			'Authorization'			=> "Bearer $token",
			'Content-Type'			=> 'application/json',
		);
		$message_response = wp_remote_post( $message_url, array( 'body' => $body, 'headers' => $headers ) );
		
		// Fehlerbehandlung Message-Request
		if($message_response['response']['code'] != 200) {
			$error = $message_response['response']['message'];
			$error_message = "Das ist leider schief gegangen: $error";
			wpforms()->process->errors[ $form_data[ 'id' ] ] [ '1' ] = esc_html__( $error_message, 'plugin-domain' );
			return;
		}
	}
	return $fields;
}
```

- `wpforms_process` - Hook:

```php
add_action( 'wpforms_process', 'sendingDataToAPI', 10, 3 );
```


