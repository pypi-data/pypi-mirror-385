// Description: Utility functions for the biomero
export const transformStructure = (data) => {
  if (!data || Object.keys(data).length === 0) {
    return {
      root: {
        index: "root",
        isFolder: true,
        children: [],
        data: "No Data Available",
        childCount: 0,
      },
    };
  }

  const items = {
    root: {
      index: "root",
      isFolder: true,
      children: [
        ...(data.projects || []).map((project) => `project-${project.id}`),
        ...(data.datasets || []).map((dataset) => `dataset-${dataset.id}`),
        ...(data.screens || []).map((screen) => `screen-${screen.id}`),
        ...(data.plates || []).map((plate) => `plate-${plate.id}`),
        "orphaned", // Include the orphaned folder
      ],
      data: "Home",
      childCount:
        (data.projects?.length || 0) +
        (data.datasets?.length || 0) +
        (data.screens?.length || 0) +
        (data.plates?.length || 0) +
        1, // Count orphaned as well
    },
    orphaned: {
      index: "orphaned",
      isFolder: true,
      children: [], // Orphaned does not have children here, but can be extended
      data: "Orphaned Images",
      childCount: data.orphaned?.childCount || 0,
      id: data.orphaned?.id || -1,
      category: "orphaned", // Add category for consistency
    },
  };

  // Add individual projects with all properties
  (data.projects || []).forEach((project) => {
    items[`project-${project.id}`] = {
      index: `project-${project.id}`,
      isFolder: project.childCount > 0,
      children: [], // Add children here if applicable
      data: project.name,
      childCount: project.childCount,
      id: project.id,
      ownerId: project.ownerId,
      permsCss: project.permsCss,
      category: "projects",
    };
  });

  // Add individual datasets with all properties
  (data.datasets || []).forEach((dataset) => {
    items[`dataset-${dataset.id}`] = {
      index: `dataset-${dataset.id}`,
      isFolder: dataset.childCount > 0,
      children: [], // Add children here if applicable
      data: dataset.name,
      childCount: dataset.childCount,
      id: dataset.id,
      ownerId: dataset.ownerId,
      permsCss: dataset.permsCss,
      category: "datasets",
    };
  });

  // Add individual screens with all properties
  (data.screens || []).forEach((screen) => {
    items[`screen-${screen.id}`] = {
      index: `screen-${screen.id}`,
      isFolder: screen.childCount > 0,
      children: [], // Add children here if applicable
      data: screen.name,
      childCount: screen.childCount,
      id: screen.id,
      ownerId: screen.ownerId,
      permsCss: screen.permsCss,
      category: "screens",
    };
  });

  // Add individual plates with all properties
  (data.plates || []).forEach((plate) => {
    items[`plate-${plate.id}`] = {
      index: `plate-${plate.id}`,
      isFolder: plate.childCount > 0,
      children: [], // Add children here if applicable
      data: plate.name,
      childCount: plate.childCount,
      id: plate.id,
      ownerId: plate.ownerId,
      permsCss: plate.permsCss,
      category: "plates",
    };
  });

  return items;
};

export const extractGroups = (htmlContent) => {
  const parser = new DOMParser();
  const doc = parser.parseFromString(htmlContent, "text/html");

  const groupElements = doc.querySelectorAll("ul#groupList li a[data-gid]");
  const groups = Array.from(groupElements).map((el) => ({
    id: parseInt(el.getAttribute("data-gid"), 10),
    name: el.textContent.trim(),
  }));

  return Array.from(new Map(groups.map((group) => [group.id, group])).values());
};
