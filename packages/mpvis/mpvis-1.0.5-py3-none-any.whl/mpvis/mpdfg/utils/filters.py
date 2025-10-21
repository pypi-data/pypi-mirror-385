import copy

def try_to_reach(source, target, skip_path, paths, visited_already, sound_activities, followed_path):
    followed_path.append(target)
    if (source, target) == skip_path:
        return False, followed_path
    elif (source in sound_activities) or ((source, target) in paths):
        return True, followed_path
    else:
        source_targets = [path[1] for path in paths if ((path[0] == source) and (path[1] not in visited_already))]
        for source_target in source_targets:
            visited_already.append(source_target)
            reached, followed_path = try_to_reach(source_target, target, skip_path, paths, visited_already, sound_activities, followed_path)
            if reached:
                return True, followed_path

    return False, followed_path

def check_soundness(activity, skip_path, remaining_paths, start_activities, end_activities, sound_activities):
    reached_source = False
    for start_activity in start_activities:
        followed_path_start = [start_activity]
        if start_activity == activity:
            reached_source = True
            break
        else:
            reached_source, followed_path_start = try_to_reach(start_activity, activity, skip_path, remaining_paths, [], sound_activities, followed_path_start)
            if reached_source:
                break

    if not reached_source:
        return False, sound_activities

    for end_activity in end_activities:
        followed_path_end = [activity]
        if end_activity == activity:
            return True, list(set(sound_activities + followed_path_start + followed_path_end))
        else:
            reached_target, followed_path_end = try_to_reach(activity, end_activity, skip_path, remaining_paths, [], sound_activities, followed_path_end)
            if reached_target:
                return True, list(set(sound_activities + followed_path_start + followed_path_end))

    return False, sound_activities

def filter_dfg_activity(activities, paths, start_activities, end_activities):
    for activity in activities.copy():
        if activity not in start_activities and activity not in end_activities:
            sources = []
            targets = []
            source_targets = {}
            target_sources = {}

            for path in paths:
                if path[0] == activity:
                    targets.append(path[1])
                if path[1] == activity:
                    sources.append(path[0])
                if path[0] not in source_targets:
                    source_targets[path[0]] = 0
                source_targets[path[0]] += 1
                if path[1] not in target_sources:
                    target_sources[path[1]] = 0
                target_sources[path[1]] += 1

            can_filter = True
            for source in sources:
                if source_targets[source] <= 1:
                    can_filter = False
                    break
            for target in targets:
                if target_sources[target] <= 1:
                    can_filter = False
                    break

            if can_filter:
                remaining_activities = activities.copy()
                del remaining_activities[activity]

                remaining_paths = {path: values for path, values in paths.items() if ((path[0] != activity) and (path[1] != activity))}

                sound_activities = []
                for remaining_activity in remaining_activities:
                    is_sound, sound_activities = check_soundness(remaining_activity, (activity, activity), remaining_paths, start_activities, end_activities, sound_activities)
                    if is_sound:
                        sound_activities.append(remaining_activity)
                    else:
                        can_filter = False
                        break

                if can_filter:
                    return remaining_activities, remaining_paths, False

    return activities, paths, True

def filter_dfg_activities(percentage, dfg, start_activities, end_activities, sort_by = "frequency", ascending = True):
    dfg_copy = copy.deepcopy(dfg)
    
    remaining_activities = dict(sorted(dfg_copy["activities"].items(), key = lambda activity: activity[1][sort_by], reverse = not ascending))
    remaining_paths = dfg_copy["connections"]

    activities_to_filter = int(len(remaining_activities) - round(len(remaining_activities) * percentage / 100, 0))

    end_reached = False
    for i in range(activities_to_filter):
        remaining_activities, remaining_paths, end_reached = filter_dfg_activity(remaining_activities, remaining_paths, start_activities, end_activities)

        if end_reached:
            break

    dfg_copy["activities"] = remaining_activities
    dfg_copy["connections"] = remaining_paths

    return dfg_copy

def filter_dfg_cycles(dfg):
    filtered_paths = {}
    remaining_paths = {}

    for path in dfg["connections"]:
        if path[0] == path[1]:
            filtered_paths[path] = dfg["connections"][path]
        else:
            remaining_paths[path] = dfg["connections"][path]

    return filtered_paths, remaining_paths

def filter_dfg_path(filtered_paths, remaining_paths, start_activities, end_activities, checked_paths):
    for path in remaining_paths.copy():
        if path not in checked_paths:
            checked_paths.append(path)
            source_count = 0
            target_count = 0
      
            for other_path in remaining_paths:
                if path[0] == other_path[0]:
                    source_count += 1
                if path[1] == other_path[1]:
                    target_count += 1
                if source_count > 1 and target_count > 1:
                    break
      
            if source_count > 1 and target_count > 1:
                reached_source, sound_activities = check_soundness(path[0], path, remaining_paths, start_activities, end_activities, [])
                reached_target, sound_activities = check_soundness(path[1], path, remaining_paths, start_activities, end_activities, sound_activities)

                if reached_source and reached_target:
                    filtered_paths[path] = remaining_paths[path]
                    del remaining_paths[path]

                    return filtered_paths, remaining_paths, False, checked_paths

    return filtered_paths, remaining_paths, True, checked_paths

def filter_dfg_paths(percentage, dfg, start_activities, end_activities, sort_by = "frequency", ascending = True):
    dfg_copy = copy.deepcopy(dfg)
    
    filtered_paths, remaining_paths = filter_dfg_cycles(dfg_copy)

    remaining_paths = dict(sorted(remaining_paths.items(), key = lambda path: path[1][sort_by], reverse = not ascending))

    end_reached = False
    checked_paths = []
    while not end_reached:
        filtered_paths, remaining_paths, end_reached, checked_paths = filter_dfg_path(filtered_paths, remaining_paths, start_activities, end_activities, checked_paths)

    filtered_paths = dict(sorted(filtered_paths.items(), key = lambda path: path[1][sort_by], reverse = ascending))
    paths_to_include = round(len(filtered_paths) * percentage / 100, 0)

    if paths_to_include > 0:
        i = 0
        for path, values in filtered_paths.items():
            remaining_paths[path] = values

            i += 1
            if i >= paths_to_include:
                break

    dfg_copy["connections"] = remaining_paths

    return dfg_copy