<!--
/content/custom/AddRecord/Content.tpl 
-->

<div class="textheader">Add Record</div>	
<!-- MOVIE-->		
	<div class="subheader" id="header"></div>

	<div class="text">
			<!--BY ID -->
			<form id="form1" action="/action" method="get">
				<input type="hidden" name="method" value="collectData">
				<input type="hidden" name="by" value="ImdbId">
				<input id="usepath" type="hidden" name="usePath" value="false">
				<input id="oldImdbId" type="hidden" name="oldImdbId" value="-1">
				<input id="form1_type" id="type" type="hidden" name="type" value="isMovie">
				<input id="path" type="hidden" name="Path" value="">
				<input id="filename" type="hidden" name="Filename" value="">
				<input id="extension" type="hidden" name="Extension" value="">
				<table align="left" >
					<tr id="tr_imdbid">
						<td id="form1_idName" width="100px">ImdbId:</td>
						<td width="400px"><input id="form1_idType" name="ImdbId" type="text" size="10"></input></td>
						<td id="form1_explain" width="100px">(e.g. tt9000000)</td>
						<td width="70px"><input id="form1_submit" type="submit" value="by ImdbId"></input></td>
					</tr>
				</table>
			</form>
			<!--BY TITLE -->
			<form id="form2" action="/alternatives" method="get">
				<input id="form2_type" type="hidden" name="type" value="">
				<input type="hidden" name="by" value="Title">
				<input type="hidden" name="modus" value="new">
				<input type="hidden" name="oldImdbId" value="-1">
				<table align="left" 
					<tr id="tr_title">
						<td width="100px">Title:</td>
						<td width="400px"><input id="title" name="Title" type="text" size="50"></input></td>
						<td width="100px">(e.g. my title)</td>
						<td width="70px"><input type="submit" value="by Title"></input></td>
					</tr>
				</table>
			</form>
			<!-- MANUAL ADD -->
			<form id="form3" action="/mediainfo" method="get">
				<input id="form3_type" type="hidden" name="type" value="">
				<input type="hidden" name="mode" value="new_record">
				<input id="ParentId" type="hidden" name="ParentId" value="">
				<table align="left" >
					<tr id="tr_title">
						<td width="100px">Information:</td>
						<td width="400px">Use this for unknown or selfrecorded records.</td>
						<td width="100px"></td>
						<td width="70px"><input type="submit" value="manual add"></input></td>
					</tr>
				</table>
			</form>

	</div>
</div>
