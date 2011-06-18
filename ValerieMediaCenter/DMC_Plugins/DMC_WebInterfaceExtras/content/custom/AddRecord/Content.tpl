<div class="textheader">Add Record</div>	
<!-- MOVIE-->		
	<div class="subheader">Movie</div>

	<div class="text">
		<table align="center" id="add_movie">
			<form id="addMovieByImdbId" action="/action" method="get">
				<input type="hidden" name="method" value="collectData">
				<input type="hidden" name="by" value="ImdbId">
				<input id="usepath" type="hidden" name="usePath" value="false">
				<input id="type" type="hidden" name="type" value="isMovie">
				<input id="path" type="hidden" name="Path" value="">
				<input id="filename" type="hidden" name="Filename" value="">
				<input id="extension" type="hidden" name="Extension" value="">
				<tr id="tr_imdbid">
					<td width="100px">ImdbId:</td>
					<td width="100px"><input id="imdbid" name="ImdbId" type="text" size="10"></input></td>
					<td width="100px">(e.g. tt9000000)</td>
					<td width="70px"><input type="submit" value="by ImdbId"></input></td>
				</tr>
			</form>
		<br><br>
			<form action="/alternatives" method="get">
				<input type="hidden" name="type" value="isMovie">
				<input type="hidden" name="by" value="Title">
				<input type="hidden" name="modus" value="new">
				<tr id="tr_title">
					<td width="100px">Title:</td>
					<td width="100px"><input id="title" name="Title" type="text" size="50"></input></td>
					<td width="100px">(e.g. my title)</td>
					<td width="70px"><input type="submit" value="by Title"></input></td>
				</tr>
			</form>
		<br><br>
			<form action="/mediainfo" method="get">
				<input type="hidden" name="type" value="isMovie">
				<input type="hidden" name="mode" value="new_record">
				<tr id="tr_title">
					<td width="100px">Information:</td>
					<td width="100px">Use this for unknown or selfrecorded records.</td>
					<td width="100px"></td>
					<td width="70px"><input type="submit" value="manual add"></input></td>
				</tr>
			</form>
		</table>
	</div>
</div>
