<script>
	// Layout component - can be used for shared UI elements like headers, navigation, etc.
	// For now, we'll keep it simple
</script>

<div class="min-h-screen bg-gray-50">
	<header class="bg-white shadow-md">
		<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
			<div class="flex justify-between h-16">
				<div class="flex">
					<div class="flex-shrink-0">
						<img class="h-8 w-8" src="https://via.placeholder.com/40" alt="JETRAG Logo">
					</div>
					<div class="hidden md:block">
						<div class="ml-10 flex items-baseline space-x-4">
							<!-- Navigation links would go here -->
							<a href="/" class="px-3 py-2 rounded-md text-sm font-medium text-gray-500 hover:text-gray-700 hover:border-indigo-300">
								Home
							</a>
							<a href="/" class="px-3 py-2 rounded-md text-sm font-medium text-gray-500 hover:text-gray-700 hover:border-indigo-300">
								About
							</a>
						</div>
					</div>
				</div>
				<div class="flex items-center">
					<!-- User profile/actions would go here -->
					<span class="text-sm font-medium text-gray-700">JETRAG</span>
				</div>
			</div>
		</div>
	</header>

	<main class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
		<!-- Page content goes here -->
		<slot />
	</main>
</div>