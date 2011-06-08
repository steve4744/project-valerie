<table align="center" id="main_table" width="100%">
	<tr>
	<td valign="top" align="center" style="background-color:#AAAAAA;">
		<br />
		<img id="duck_img" src="" width="78" height="107" alt="n/a"></img>
		<br /><br />
		<img id="duck_backdrop_img" src="" width="160" height="90" alt="n/a"></img>
	</td>
	<td>
		<table align="center" id="details_table">
			<form action="/action" method="get">
				<input type="hidden" name="method" value="edit">
				<input type="hidden" name="what" value="">
				<tr><td></td></tr>
				<tr id="tr_type"><td>*Type:</td><td id="td_type"><input id="type" name="Type" type="text" size="10" disabled="disabled"></input></td></tr> 
				<tr id="tr_imdbid"><td>*ImdbId:</td><td><input id="imdbid" name="imdbid" type="text" size="10"></input></td><td>(e.g. tt9000000)</td></tr>
				<tr id="tr_thetvdbid"><td>TheTvDbId:</td><td><input id="thetvdbid" name="thetvdbid" type="text" size="10"></input></td><td>(e.g. 999999)</td></tr>
				<tr id="tr_title"><td>*Title:</td><td><input id="title" name="Title" type="text" size="50"></input></td><td>(e.g. my title)</td></tr>
				<tr id="tr_tag"><td>Tag:</td><td><input id="tag" name="Tag" type="text" size="50"></input></td><td>(e.g.my tag)</td></tr>
				<tr id="tr_season"><td>Season:</td><td><input id="season" name="season" type="text" size="2" maxlength="2"></input></td><td>(e.g. 01)</td></tr>
				<tr id="tr_episode"><td>Episode:</td><td><input id="episode" name="episode" type="text" size="3" maxlength="3"></input></td><td>(e.g. 01)</td></tr>
				<tr id="tr_plot"><td>Plot:</td><td><textarea id="plot" name="Plot" cols="50" rows="15"></textarea></td><td>(e.g. story description)</td></tr>
				<tr id="tr_runtime"><td>*Runtime:</td><td><input id="runtime" name="Runtime" type="text" size="50"></input></td><td>(e.g. 90)</td></tr>
				<tr id="tr_year"><td>*Year:</td><td><input id="year" name="Year" type="text" size="4" maxlength="4"></td><td></input>(e.g. 2011)</td></tr>
				<tr id="tr_genres"><td>Genres:</td><td><input id="genres" name="Genres" type="text" size="50"></input></td><td>(e.g. Action|Thriller)</td></tr>
				<tr id="tr_popularity"><td>*Popularity:</td><td><input id="popularity" name="Popularity" type="text" size="50"></input></td><td>(e.g. 9)</td></tr>
				<tr id="tr_path"><td>*Path:</td><td><input id="path" name="Path" type="text" size="50"></td><td></input>(e.g. /some/where/on/my/box/)</td></tr>
				<tr id="tr_filename"><td>*Filename:</td><td><input id="filename" name="Filename" type="text" size="35"></td><td></input>(e.g. my filename)</td></tr>
				<tr id="tr_extension"><td>*Extension:</td><td><input id="extension" name="Extension" type="text" size="4" maxlength="3"></td><td></input>(without leading . => e.g. mkv)</td></tr>		
				<tr><td><input type="submit" value="Save"></input></td></tr>
			</form>
		</table>
	</td></tr>
</table>
