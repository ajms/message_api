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

add_action( 'template_redirect', 'redirectCodeToToken' );

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

add_action( 'wpforms_process', 'sendingDataToAPI', 10, 3 );
