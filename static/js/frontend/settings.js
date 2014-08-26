var companyData;

$( document ).ready(function(){
	loadSettings();
	setUpButtons();
});

function setUpButtons(){

	$('#TestDomainButton').click(function(){
		var domain = $('#DomainName').val();
		$('#DomainTestingImage').removeClass('hidden');
		$('#DomainTestingImage').addClass('show');
		$('#DomainTestResultDiv').removeClass();
		$('#DomainTestResultDiv').addClass('hidden');

		$.get("http://" + domain + "/TestDomainRedirection", function(data){
			console.log("Domain Test Successful!");
			$('#DomainTestingImage').removeClass('show');
			$('#DomainTestingImage').addClass('hidden');
			$('#DomainTestResultDiv').removeClass();

			$('#DomainTestResultDiv').addClass('alert-success');
			$('#DomainTestResultDiv').addClass('alert');
			$('#DomainTestResultDiv').text("Domain is currently redirected!")

		}).error(function(err){
			console.log("Domain not correctly redirected");
			$('#DomainTestingImage').removeClass('show');
			$('#DomainTestingImage').addClass('hidden');
			$('#DomainTestResultDiv').removeClass();

			$('#DomainTestResultDiv').addClass('alert-danger');
			$('#DomainTestResultDiv').addClass('alert');
			$('#DomainTestResultDiv').text("Domain is not redirected to 173.194.110.226")
		});
	});

	$('#AddEditDomainButton').click(function(){
		console.log("Submitting domain form...");
		$('#AddEditDomainForm').attr('action', '/Post/AddEditDomain/');
		$('#AddEditDomainForm').submit();
	});

	$('#DeleteDomainButton').click(function(){
		console.log("Submitting delete domain form...");
		$('#AddEditDomainForm').attr('action', '/Post/DeleteDomain/');
		$('#AddEditDomainForm').submit();
	});

	$('#AddUserButton').click(function(){
		console.log("Submitting add user invite form...");
		$('#AddRemoveUserRequestForm').attr('action', '/Post/AddUserInvite/');
		$('#AddRemoveUserRequestForm').submit();
	});

	$('#DeleteInterstitialButton').click(function(){
		console.log("Submitting delete interstitial form...");
		$('#AddEditInterstitialForm').attr('action', '/Post/DeleteInterstitial/');
		$('#AddEditInterstitialForm').submit();
	});

	$('#AddEditInterstitialButton').click(function(){
		console.log("Submitting add/edit interstitial form...");
		$('#AddEditInterstitialForm').attr('action', '/Post/AddEditInterstitial/');
		$('#AddEditInterstitialForm').submit();
	});

	$('#DeleteUserButton').click(function(){
		console.log("Submitting add/edit interstitial form...");
		$('#AddRemoveUserForm').attr('action', '/Post/RevokeUserAccount/');
		$('#AddRemoveUserForm').submit();
	});
}

function loadSettings(){
	$.get('/api/CompanySettings', function(data){
		console.log("Got company data");
		console.log(data);
		companyData = data;
		$('#CompanyName').text(data.Name);
		loadUsers(companyData.Users, companyData.PendingUsers);
		loadDomains(companyData.Domains);
		loadInterstitials(companyData.Intersticials);
		loadTextFromPackageLevel(data);
	});
}

function loadInterstitials (interstitials) {
	for (var i = interstitials.length - 1; i >= 0; i--) {
		var intersticial = interstitials[i];
		var rowArr = [intersticial.Name, intersticial.Url, intersticial.DisplayChance, intersticial.Active ? "Yes" : "No"];
		var row = addRowToTable("Interstitial" + intersticial.id, "#IntersticialRows", rowArr, "int-name='" + 
			intersticial.Name  + "' int-id='" + intersticial.id + "' int-chance='" + intersticial.DisplayChance + 
			"' int-active='" + intersticial.Active + "' int-url='" + intersticial.Url + "'");
		row.click(function (e) {
			var interId = $('#' + e.currentTarget.id).attr("int-id");
			var name = $('#' + e.currentTarget.id).attr("int-name");
			var chance = $('#' + e.currentTarget.id).attr("int-chance");
			var url = $('#' + e.currentTarget.id).attr("int-url");
			var active = $('#' + e.currentTarget.id).attr("int-active");
			$('#InterstitialName').val(name);
			$('#DisplayChance').val(chance);
			$('#InterstitialUrl').val(url);
			$('#InterstitialActive').prop('checked', active == 'true');
			$('#InterstitialId').prop('value', interId);
			$('#AddEditInterstitialModal').modal('show');
		});
		$('#DomainInterstititalOption').append("<option value='" + intersticial.id + "'>" + intersticial.Name + "</option>")
	}
}

//Users
function loadUsers(users, pendingUsers){
	$('#UserRows').empty();
	for (var i = pendingUsers.length - 1; i >= 0; i--) {
		var user = pendingUsers[i];
		var rowArr = ["", user.Email, "No", "NA"];
		var row = addRowToTable("User" + user.id, "#UserRows", rowArr);
		row.click(function(e){
			console.log(user.id);
		});
	}
	for (var i = users.length - 1; i >= 0; i--) {
		var user = users[i];
		var rowArr = [user.Username, user.Email, "Yes", (user.IsAdmin ? "Yes" : "No")];
		var row = addRowToTable("User" + user.id, "#UserRows", rowArr, " username='" + user.Username + "' userid='" + user.id + "' is-admin='" + user.IsAdmin + "'");
		row.click(function(e){
			var userId = $('#' + e.currentTarget.id).attr("userid");
			var username = $('#' + e.currentTarget.id).attr("username");
			var admin = $('#' + e.currentTarget.id).attr("is-admin");
			$('#userid').val(userId);
			$('#UserIsAdmin').prop('checked', admin);
			$('#EditDeleteUsername').text(username);
			$('#EditDeleteUserModal').modal('show');
		});
	};
}

//Package Level Loading
function loadTextFromPackageLevel(company){
	switch(company.PackageLevel){
		case 2:
			loadBasicPackage(company);
			break;
		case 3:
			loadProPackage(company);
			break;
		case 4:
			loadEnterprisePackage(company);
			break;
	}
}

function loadBasicPackage(company){
	$('#UserInvitesButton').text("Invites Left: None");
	$('#UserInvitesButton').click(function(e){
		//Show Upsell button for users
		console.log("Showing user upsell button...");
	});
	$('#DomainInterstitialGroup').hide();
	$('#AddDomainButton').text("Domains Left: " + (2 - company.Domains.length));
	$('#AddDomainButton').click(function(e){
		//Show Domain Upsell button
		if(company.Domains.length == 1){
			console.log("Showing domain upsell button");
		}else{
			showNewDomainModal();
		}
	});

	//Show report ant intersticial overllays
	$('#ReportSection').empty();
	$('#ReportSection').append("<img id='ReportUpgrade' src='/static/img/upgrade_to_reports.png' />")
	$('#IntersticialSection').empty();
	$('#IntersticialSection').append("<img id='IntersticialUpgrade' src='/static/img/upgrade_to_intersticials.png' />")
}

function loadProPackage(company){
	$('#UserInvitesButton').text("Invites Left: " + (5 - company.Users.length));
	$('#UserInvitesButton').click(function(e){
		if(company.Users.length == 5){
			console.log("Showing user upsell button...");
		}else{
			$('#AddUserModal').modal('show');
		}
	});

	$('#DomainInterstitialGroup').show();
	$('#AddDomainButton').text("Domains Left: " + (5 - company.Domains.length));
	$('#AddDomainButton').click(function(e){
		//Show Domain Upsell button
		if(company.Domains.length >= 5){
			console.log("Showing domain upsell button");
		}else{
			showNewDomainModal();
		}
	});

	$('#AddIntersticialButton').click(function(e){
		$('#AddEditInterstitialModal').modal();
	});

}

function loadEnterprisePackage(company){
	//TODO
	loadProPackage(company);
}

function showNewInterstitialModal(){}

function showNewDomainModal(){
	$('#DomainName').val('');
	$("#DomainInterstititalOption").val('-1');
	$("#DomainId").val('-1');
	$('#EditDomainModal').modal(); 
}

//Domains
function loadDomains(domains){
	$('#DomainRows').empty();
	for (var i = domains.length - 1; i >= 0; i--) {
		var domain = domains[i];
		var interstitialNil = "No";
		if(domains.intersticial != null){
			interstitialNil = "Yes";
		}
		//TODO Configured
		var rowArr = [domain.Domain, "NA", interstitialNil];
		var row = addRowToTable('Domain' + domain.id, "#DomainRows", rowArr, "domain='" + domain.Domain + "' domainId='" + domain.id + "' inter-id='" + (domain.Intersticial ? domain.Intersticial.id : '-1') + "'");
		row.click(function (e){
			var mDomain = $('#' + e.currentTarget.id).attr("domain");
			var mDomainId = $('#' + e.currentTarget.id).attr("domainId");
			var interId = $('#' + e.currentTarget.id).attr("inter-id");
			$('#DomainName').val(mDomain);
			$('#DomainId').val(mDomainId);
			$('#DomainInterstititalOption').val(interId);
			$('#EditDomainModal').modal(); 
		});
	}
}

//Reports
function runReport(reportId){

}

function saveIntersticial(intersticial){

}

function addRowToTable(rowID, table, values){
	addRowToTable(rowID, table, values, "");
}

function addRowToTable(rowID, table, values, rowExtra){
	//Frist, clear table
	var row = "<tr id='" + rowID + "'" + rowExtra + " >";
	for (var i = 0; i < values.length; i++) {
		row += "<td>" + values[i] + "</td>";
	};
	row += "</tr>";
	$(table).append(row);
	return $("#" + rowID);
}